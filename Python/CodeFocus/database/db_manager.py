import datetime
from peewee import *
from peewee import fn

# Cấu hình DB
db = SqliteDatabase('codefocus.db', pragmas={'journal_mode': 'wal'})


# --- MODELS ---
class BaseModel(Model):
    class Meta:
        database = db


class Session(BaseModel):
    start_time = DateTimeField(default=datetime.datetime.now)
    end_time = DateTimeField(null=True)
    duration = IntegerField(default=0)
    mode = CharField(default='Pomodoro')
    is_completed = BooleanField(default=False)


class ActivityLog(BaseModel):
    session = ForeignKeyField(Session, backref='logs', on_delete='CASCADE')
    timestamp = DateTimeField(default=datetime.datetime.now)
    process_name = CharField()
    window_title = CharField(null=True)
    url = CharField(null=True)
    category = CharField(default='Work')


class Blacklist(BaseModel):
    value = CharField(unique=True)
    type = CharField()
    created_at = DateTimeField(default=datetime.datetime.now)


class Settings(BaseModel):
    key = CharField(unique=True)
    value = CharField()


# --- INITIALIZE ---
def initialize_db():
    db.connect()
    db.create_tables([Session, ActivityLog, Blacklist, Settings], safe=True)
    default_settings = {'pomodoro_minutes': '25', 'break_minutes': '5', 'grace_period_seconds': '60'}
    for key, val in default_settings.items():
        if not Settings.select().where(Settings.key == key).exists():
            Settings.create(key=key, value=val)
    seed_sample_data()

# --- SETTINGS & BLACKLIST ---
def get_setting(key, default):
    try:
        return Settings.get(Settings.key == key).value
    except:
        return default


def update_setting(key, value):
    Settings.replace(key=key, value=str(value)).execute()


def get_blacklist():
    try:
        apps = [b.value for b in Blacklist.select().where(Blacklist.type == 'app')]
        urls = [b.value for b in Blacklist.select().where(Blacklist.type == 'url')]
        if not apps and not urls: return (['league of legends'], ['facebook', 'youtube', 'tiktok'])
        return apps, urls
    except:
        return [], []


def add_to_blacklist(value, type_):
    try:
        Blacklist.create(value=value.lower(), type=type_); return True
    except:
        return False


def remove_from_blacklist(value):
    try:
        Blacklist.delete().where(Blacklist.value == value).execute(); return True
    except:
        return False


# --- SESSION & LOGGING ---
def create_session(mode='Pomodoro'):
    return Session.create(mode=mode, start_time=datetime.datetime.now())


def end_session(session_id, duration_seconds, is_completed=False):
    try:
        s = Session.get_by_id(session_id)
        s.end_time = datetime.datetime.now()
        s.duration = duration_seconds
        s.is_completed = is_completed
        s.save()
    except:
        pass


def log_activity(session_id, process, title, url=None, category='Work'):
    try:
        if session_id:
            ActivityLog.create(session_id=session_id, process_name=process, window_title=title, url=url,
                               category=category)
    except Exception as e:
        print(f"Log Error: {e}")


# --- REPORT & STATS (CÁC HÀM QUAN TRỌNG) ---

def format_date_str(date_input):
    """Helper: Chuyển đổi mọi định dạng ngày về chuỗi YYYY-MM-DD"""
    if isinstance(date_input, datetime.date) or isinstance(date_input, datetime.datetime):
        return date_input.strftime("%Y-%m-%d")
    return str(date_input)  # Nếu là string thì giữ nguyên


def get_today_stats():
    """Thống kê nhanh cho biểu đồ tròn Dashboard"""
    try:
        today = datetime.date.today()
        start = datetime.datetime.combine(today, datetime.time.min)
        end = datetime.datetime.combine(today, datetime.time.max)

        work = ActivityLog.select().where((ActivityLog.timestamp >= start) & (ActivityLog.timestamp <= end) & (
                    ActivityLog.category == 'Work')).count()
        distraction = ActivityLog.select().where((ActivityLog.timestamp >= start) & (ActivityLog.timestamp <= end) & (
                    ActivityLog.category == 'Distraction')).count()
        return {'work': work, 'distraction': distraction}
    except:
        return {'work': 0, 'distraction': 0}


def get_total_work_time_str(date_obj):
    """Tính tổng thời gian làm việc trong ngày -> Trả về chuỗi hiển thị"""
    try:
        target = format_date_str(date_obj)
        # Chỉ tính session đã hoàn thành hoặc có duration > 0
        sessions = Session.select().where((fn.date(Session.start_time) == target) & (Session.mode == 'Pomodoro'))
        total_sec = sum([s.duration for s in sessions])
        total_min = total_sec // 60

        h = total_min // 60
        m = total_min % 60
        return f"{h} giờ {m} phút", total_min
    except:
        return "0 phút", 0


def get_daily_breakdown(date_obj):
    """Lấy danh sách Session và Top Apps"""
    target = format_date_str(date_obj)

    # 1. Sessions
    sessions = Session.select().where(fn.date(Session.start_time) == target)

    # 2. Apps Stats (Group by Window Title)
    app_stats = (ActivityLog
                 .select(ActivityLog.window_title, ActivityLog.process_name, ActivityLog.category,
                         fn.COUNT(ActivityLog.id).alias('count'))
                 .where(fn.date(ActivityLog.timestamp) == target)
                 .group_by(ActivityLog.window_title)
                 .order_by(fn.COUNT(ActivityLog.id).desc())
                 .limit(15))

    return sessions, app_stats


def get_daily_health_report(date_obj):
    """Phân tích sức khoẻ"""
    target = format_date_str(date_obj)

    # Query tổng
    total_work_query = Session.select(fn.SUM(Session.duration)).where(
        (fn.date(Session.start_time) == target) & (Session.mode == 'Pomodoro')).scalar()
    total_work_min = (total_work_query or 0) // 60

    distraction_count = ActivityLog.select().where(
        (fn.date(ActivityLog.timestamp) == target) & (ActivityLog.category == 'Distraction')).count()

    # Logic lời khuyên
    advice = "Ngày làm việc bình thường."
    color = "#3b82f6"

    if total_work_min == 0:
        advice = "Chưa có dữ liệu làm việc hôm nay."
        color = "#94a3b8"
    elif total_work_min > 480:
        advice = "⚠️ CẢNH BÁO: Bạn đã làm quá 8 tiếng! Hãy nghỉ ngơi ngay."
        color = "#ef4444"
    elif distraction_count > 20:
        advice = f"📉 Mất tập trung: Bạn tốn ~{distraction_count} phút cho việc xao nhãng."
        color = "#f59e0b"
    else:
        advice = "✅ Phong độ tuyệt vời! Bạn làm việc rất tập trung."
        color = "#10b981"

    return {'advice': advice, 'color': color}


def get_historical_data(days=7):
    """Lấy dữ liệu cho biểu đồ đường (Đã sửa lỗi hiển thị 0)"""
    try:
        # 1. Xác định ngày bắt đầu (chuyển về datetime để so sánh chính xác với DateTimeField)
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=days)
        # Chuyển start_date thành datetime (00:00:00) để so sánh trong DB
        start_datetime = datetime.datetime.combine(start_date, datetime.time.min)

        # 2. Khởi tạo dictionary kết quả với giá trị 0 cho tất cả các ngày
        result = {}
        for i in range(days + 1):  # +1 để lấy cả ngày hôm nay
            d = start_date + datetime.timedelta(days=i)
            # Key phải là chuỗi YYYY-MM-DD chuẩn
            result[d.strftime("%Y-%m-%d")] = 0

        # 3. Truy vấn DB - Sử dụng strftime để ép kiểu ngày tháng chính xác
        # Cú pháp SQLite: strftime('%Y-%m-%d', column)
        day_col = fn.strftime('%Y-%m-%d', Session.start_time)

        query = (Session
                 .select(day_col.alias('day_str'), fn.SUM(Session.duration).alias('total_sec'))
                 .where(
            (Session.start_time >= start_datetime) &
            (Session.mode == 'Pomodoro')
        )
                 .group_by(day_col)
                 .order_by(day_col))

        # 4. Map dữ liệu từ DB vào dictionary
        for item in query:
            # item.day_str sẽ trả về chuỗi '2025-12-22'
            date_key = item.day_str
            minutes = (item.total_sec or 0) // 60

            if date_key in result:
                result[date_key] = minutes

        return result

    except Exception as e:
        print(f"Lỗi Chart Data: {e}")
        return {}


# --- HÀM TẠO DỮ LIỆU MẪU (NÂNG CẤP) ---
def seed_sample_data():
    """Tạo dữ liệu giả 30 ngày để test các trường hợp báo cáo"""

    # Chỉ tạo nếu chưa có dữ liệu Session
    if Session.select().count() > 0:
        print("⚠️ Dữ liệu đã tồn tại, bỏ qua việc tạo mẫu.")
        return

    import random
    print("⏳ Đang tạo dữ liệu mẫu... Vui lòng đợi...")

    today = datetime.datetime.now()

    # Danh sách các app giả lập
    work_apps = ["PyCharm", "Visual Studio Code", "StackOverflow", "Document.docx", "Figma"]
    distract_apps = ["Facebook", "YouTube", "TikTok", "Netflix", "League of Legends"]

    # Hàm phụ trợ để tạo 1 phiên làm việc
    def create_fake_session(date_obj, duration_min, is_distracted=False):
        # Tạo Session
        s = Session.create(
            start_time=date_obj,
            end_time=date_obj + datetime.timedelta(minutes=duration_min),
            duration=duration_min * 60,  # Đổi sang giây
            mode='Pomodoro',
            is_completed=True
        )

        # Tạo Activity Log (Mỗi phút 1 log)
        for i in range(duration_min):
            log_time = date_obj + datetime.timedelta(minutes=i)

            # Logic: Nếu là phiên xao nhãng, 70% log là app chơi bời
            if is_distracted and random.random() < 0.7:
                cat = 'Distraction'
                app = random.choice(distract_apps)
            else:
                cat = 'Work'
                app = random.choice(work_apps)

            ActivityLog.create(
                session=s,
                timestamp=log_time,
                process_name=app + ".exe",
                window_title=f"{app} - Window",
                category=cat
            )

    # --- KỊCH BẢN 1: HÔM NAY - PHONG ĐỘ TUYỆT VỜI (Green) ---
    # Làm 4 tiếng, ít xao nhãng
    base_time = today.replace(hour=8, minute=0)
    for _ in range(4):  # 4 session x 60p
        create_fake_session(base_time, 60, is_distracted=False)
        base_time += datetime.timedelta(minutes=75)  # Nghỉ 15p

    # --- KỊCH BẢN 2: HÔM QUA - MẤT TẬP TRUNG (Orange) ---
    # Làm ít, chơi nhiều (Distraction count > 20)
    yesterday = today - datetime.timedelta(days=1)
    base_time = yesterday.replace(hour=9, minute=0)
    for _ in range(3):
        create_fake_session(base_time, 45, is_distracted=True)  # Set flag distracted
        base_time += datetime.timedelta(minutes=60)

    # --- KỊCH BẢN 3: HÔM KIA - LÀM VIỆC QUÁ SỨC (Red) ---
    # Làm > 8 tiếng (480 phút)
    day_minus_2 = today - datetime.timedelta(days=2)
    base_time = day_minus_2.replace(hour=7, minute=0)
    # Tạo 10 session, mỗi session 50 phút = 500 phút
    for _ in range(10):
        create_fake_session(base_time, 50, is_distracted=False)
        base_time += datetime.timedelta(minutes=55)

    # --- KỊCH BẢN 4: 27 NGÀY CÒN LẠI (RANDOM) ---
    for i in range(3, 30):
        target_date = today - datetime.timedelta(days=i)

        # Random: 20% là ngày nghỉ (không tạo data)
        if random.random() < 0.2:
            continue

        # Random số session trong ngày (2 đến 6 session)
        num_sessions = random.randint(2, 6)
        start_hour = random.randint(8, 14)
        base_time = target_date.replace(hour=start_hour, minute=0)

        for _ in range(num_sessions):
            dur = random.randint(25, 45)
            # 10% cơ hội là phiên xao nhãng
            is_bad = random.random() < 0.1
            create_fake_session(base_time, dur, is_distracted=is_bad)
            base_time += datetime.timedelta(minutes=dur + 10)

    print("✅ Đã tạo xong dữ liệu mẫu cho 30 ngày!")