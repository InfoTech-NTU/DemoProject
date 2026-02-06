package ntu.nguyentruong.smartrecipeapp;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.CheckBox;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.bumptech.glide.Glide;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.firestore.DocumentReference;
import com.google.firebase.firestore.FieldValue;
import com.google.firebase.firestore.FirebaseFirestore;

import java.util.List;

public class DetailActivity extends AppCompatActivity {
    private ImageView imgDetailFood;
    private TextView tvDetailName, tvDetailTime,tvDetailServe,tvLikeCount, tvDetailDifficulty;
    private LinearLayout layoutIngredientsList, layoutStepsList;
    private ImageButton btnBackDetail, btnSaveFavorite;
    private MonAn monAnHienTai;
    private FirebaseFirestore db;
    private FirebaseUser currentUser;
    private boolean isLiked = false;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_detail);
        // 1. Khởi tạo Firebase
        db = FirebaseFirestore.getInstance();
        currentUser = FirebaseAuth.getInstance().getCurrentUser();
        // 2. Khởi tạo các view
        initViews();
        getDataFromIntent();

        if (monAnHienTai != null) {
            setupUI();
            checkFavoriteStatus();
            handleEvents();
        } else {
            Toast.makeText(this, "Không tìm thấy dữ liệu món ăn", Toast.LENGTH_SHORT).show();
            finish();
        }

    }
    private void initViews() {
        imgDetailFood = findViewById(R.id.imgDetailFood);
        tvDetailName = findViewById(R.id.tvDetailName);
        tvDetailTime = findViewById(R.id.tvDetailTime);
        tvDetailServe = findViewById(R.id.tvDetailServe);
        tvLikeCount = findViewById(R.id.tvLikeCount);
        tvDetailDifficulty = findViewById(R.id.tvDetailDifficulty);

        layoutIngredientsList = findViewById(R.id.layoutIngredientsList);
        layoutStepsList = findViewById(R.id.layoutStepsList);

        btnBackDetail = findViewById(R.id.btnBackDetail);
        btnSaveFavorite = findViewById(R.id.btnSaveFavorite);
    }

    private void getDataFromIntent() {
        Intent intent = getIntent();
        if (intent != null && intent.hasExtra("object_monan")) {
            monAnHienTai = (MonAn) intent.getSerializableExtra("object_monan");
        }
    }

    private void setupUI() {
        // 1. Hiển thị thông tin cơ bản
        tvDetailName.setText(monAnHienTai.getTenMon());
        tvDetailTime.setText("⏱ " + monAnHienTai.getThoiGian());
        if(tvDetailServe != null) {
            tvDetailServe.setText("👥 " + monAnHienTai.getKhauPhan());
        }
        String doKho = monAnHienTai.getDoKho();
        if (doKho != null && !doKho.isEmpty()) {
            tvDetailDifficulty.setText("⭐ " + doKho);
            tvDetailDifficulty.setVisibility(View.VISIBLE);

            // Đổi màu chữ theo độ khó
            if (doKho.equals("Khó")) {
                tvDetailDifficulty.setTextColor(android.graphics.Color.RED);
            } else if (doKho.equals("Trung bình")) {
                tvDetailDifficulty.setTextColor(android.graphics.Color.parseColor("#FF9800")); // Màu Cam
            } else {
                tvDetailDifficulty.setTextColor(android.graphics.Color.parseColor("#4CAF50")); // Màu Xanh lá
            }
        } else {

            tvDetailDifficulty.setVisibility(View.GONE);
        }
        updateLikeCountUI(monAnHienTai.getLikeCount());

        // 2. Load ảnh từ URL bằng Glide
        Glide.with(this)
                .load(monAnHienTai.getHinhAnh())
                .placeholder(R.drawable.bg_rounded_pink)
                .error(R.drawable.bg_rounded_launch)
                .into(imgDetailFood);

        // 3. Xử lý danh sách Nguyên liệu
        layoutIngredientsList.removeAllViews();
        List<String> nguyenLieus = monAnHienTai.getNguyenLieu();

        if (nguyenLieus != null) {
            for (String item : nguyenLieus) {
                CheckBox checkBox = new CheckBox(this);
                checkBox.setText(item);
                checkBox.setTextColor(getResources().getColor(android.R.color.black));
                layoutIngredientsList.addView(checkBox);
            }
        }

        // 4. Xử lý danh sách Cách làm
        layoutStepsList.removeAllViews();
        List<String> cachLams = monAnHienTai.getCachLam();
        LayoutInflater inflater = LayoutInflater.from(this);

        if (cachLams != null) {
            for (int i = 0; i < cachLams.size(); i++) {
                View stepView = inflater.inflate(R.layout.item_step_food, layoutStepsList, false);

                TextView tvNum = stepView.findViewById(R.id.tvStepNumber);
                TextView tvContent = stepView.findViewById(R.id.tvStepContent);

                tvNum.setText(String.valueOf(i + 1));
                tvContent.setText(cachLams.get(i));

                layoutStepsList.addView(stepView);
            }
        }

    }
    private void updateLikeCountUI(int count) {
        tvLikeCount.setText(count + " yêu thích");
    }
    private void handleEvents() {
        btnBackDetail.setOnClickListener(v -> finish());
        btnSaveFavorite.setOnClickListener(v -> {
            // Đảo trạng thái like
            isLiked = !isLiked;
            // Xử lý số lượng hiển thị NGAY LẬP TỨC
            int currentCount = monAnHienTai.getLikeCount();
            if (isLiked) {
                currentCount++;
            } else {
                currentCount--;
            }
            monAnHienTai.setLikeCount(currentCount);

            // Cập nhật giao diện
            updateUIButton(isLiked);
            updateLikeCountUI(currentCount);

            // Gửi dữ liệu lên Firestore
            updateFavoriteToFirestore(isLiked);
        });
    }
    private void updateUIButton(boolean liked) {
        if (liked) {
            btnSaveFavorite.setImageResource(R.drawable.ic_heart_fill);
            Toast.makeText(this, "Đã thêm vào yêu thích", Toast.LENGTH_SHORT).show();
        } else {
            btnSaveFavorite.setImageResource(R.drawable.ic_heart_outline);
            Toast.makeText(this, "Đã bỏ yêu thích", Toast.LENGTH_SHORT).show();
        }
    }


    private void updateFavoriteToFirestore(boolean isAdding) {
        String myUid = currentUser.getUid();
        String docId = monAnHienTai.getId();

        if (docId == null || docId.isEmpty()) {
            Log.e("FAVORITE", "Lỗi: Document ID bị null");
            return;
        }

        // 1. Tham chiếu đến món ăn trong collection "recipes"
        DocumentReference recipeRef = db.collection("recipes").document(docId);

        // 2. Tham chiếu đến bảng "favorites"
        String favoriteDocId = myUid + "_" + docId;
        DocumentReference favRef = db.collection("favorites").document(favoriteDocId);

        if (isAdding) {
            // --- TRƯỜNG HỢP THÍCH ---

            // A. Cập nhật bảng Recipes (tăng likeCount, thêm uid vào mảng)
            recipeRef.update("likedBy", FieldValue.arrayUnion(myUid),
                    "likeCount", FieldValue.increment(1));

            // B. Tạo dữ liệu mới trong bảng Favorites
            java.util.Map<String, Object> favData = new java.util.HashMap<>();
            favData.put("userId", myUid);
            favData.put("recipeId", docId);
            favData.put("timestamp", FieldValue.serverTimestamp());

            favRef.set(favData)
                    .addOnFailureListener(e -> {
                        Log.e("FAV_ERROR", "Không lưu được vào favorites: " + e.getMessage());
                    });

        } else {
            // --- TRƯỜNG HỢP BỎ THÍCH ---

            // A. Cập nhật bảng Recipes (giảm likeCount, xóa uid khỏi mảng)
            recipeRef.update("likedBy", FieldValue.arrayRemove(myUid),
                    "likeCount", FieldValue.increment(-1));

            // B. Xóa dữ liệu khỏi bảng Favorites
            favRef.delete();
        }
    }
    private void checkFavoriteStatus() {
        if (currentUser == null) return;

        String myUid = currentUser.getUid();

        // Kiểm tra danh sách likedBy có chứa UID của mình không
        if (monAnHienTai.getLikedBy() != null && monAnHienTai.getLikedBy().contains(myUid)) {
            isLiked = true;
            btnSaveFavorite.setImageResource(R.drawable.ic_heart_fill);
        } else {
            isLiked = false;
            btnSaveFavorite.setImageResource(R.drawable.ic_heart_outline);
        }
    }
}