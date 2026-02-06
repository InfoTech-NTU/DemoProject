package ntu.nguyentruong.recipesadmin;

import android.content.Context;
import android.util.Log;

import com.google.firebase.firestore.FirebaseFirestore;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

public class DataSeeder {

    public static void seedRecipes(Context context) {
        FirebaseFirestore db = FirebaseFirestore.getInstance();

        try {
            InputStream is = context.getAssets().open("100_mon_an.json");
            int size = is.available();
            byte[] buffer = new byte[size];
            is.read(buffer);
            is.close();

            String json = new String(buffer, StandardCharsets.UTF_8);
            JSONArray array = new JSONArray(json);

            for (int i = 0; i < array.length(); i++) {
                JSONObject obj = array.getJSONObject(i);

                Map<String, Object> map = new HashMap<>();
                Iterator<String> keys = obj.keys();
                while (keys.hasNext()) {
                    String key = keys.next();
                    Object value = obj.get(key); // Lấy giá trị ra

                    // Kiểm tra nếu giá trị là một JSONArray
                    if (value instanceof JSONArray) {
                        // Chuyển đổi JSONArray thành List và đưa vào map
                        map.put(key, toList((JSONArray) value));
                    } else if (value instanceof JSONObject) {
                        // Nếu có cả object lồng nhau thì chuyển đổi
                        map.put(key, toMap((JSONObject) value));
                    }
                    else {
                        // Nếu là kiểu dữ liệu cơ bản (String, int, boolean...) thì giữ nguyên
                        map.put(key, value);
                    }
                }

                db.collection("recipes").add(map)
                        .addOnSuccessListener(documentReference -> Log.d("SEED", "Thêm thành công món: " + map.get("tenMon")))
                        .addOnFailureListener(e -> Log.e("SEED", "Lỗi khi thêm món ăn", e));
            }

            Log.d("SEED", "Bắt đầu quá trình import " + array.length() + " món ăn.");

        } catch (Exception e) {
            Log.e("SEED", "Lỗi seed", e);
        }
    }

    /**
     * Hàm trợ giúp để chuyển đổi một JSONArray thành List<Object>.
     */
    public static List<Object> toList(JSONArray array) throws JSONException {
        List<Object> list = new ArrayList<>();
        for (int i = 0; i < array.length(); i++) {
            Object value = array.get(i);
            if (value instanceof JSONArray) {
                value = toList((JSONArray) value); // Đệ quy nếu mảng lồng mảng
            } else if (value instanceof JSONObject) {
                value = toMap((JSONObject) value); // Đệ quy nếu có object trong mảng
            }
            list.add(value);
        }
        return list;
    }

    /**
     * (Tùy chọn) Hàm trợ giúp để chuyển đổi JSONObject thành Map<String, Object>.
     * Cần thiết nếu JSON của bạn có các đối tượng lồng nhau.
     */
    public static Map<String, Object> toMap(JSONObject object) throws JSONException {
        Map<String, Object> map = new HashMap<>();
        Iterator<String> keys = object.keys();
        while (keys.hasNext()) {
            String key = keys.next();
            Object value = object.get(key);
            if (value instanceof JSONArray) {
                value = toList((JSONArray) value);
            } else if (value instanceof JSONObject) {
                value = toMap((JSONObject) value);
            }
            map.put(key, value);
        }
        return map;
    }
}
