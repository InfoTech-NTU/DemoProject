package ntu.nguyentruong.recipesadmin;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
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
import com.google.android.material.button.MaterialButton;
import com.google.firebase.firestore.FirebaseFirestore;

import java.util.List;

public class DetailRecipesActivity extends AppCompatActivity {

    private ImageView imgDetail;
    private TextView tvName, tvIngredients, tvDetailTime,tvDetailServe,tvDetailDifficulty;
    private MaterialButton btnApprove, btnReject;
    private LinearLayout  layoutStepsList;

    private FirebaseFirestore db;
    private String recipeId;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_detail_recipes);

        db = FirebaseFirestore.getInstance();
        recipeId = getIntent().getStringExtra("RECIPE_ID");

        initViews();
        loadData();
        setupActions();
    }

    private void initViews() {
        imgDetail = findViewById(R.id.imgDetailFood);
        tvName = findViewById(R.id.tvDetailName);
        tvIngredients = findViewById(R.id.tvIngredientsList);
        btnApprove = findViewById(R.id.btnApprove);
        btnReject = findViewById(R.id.btnReject);
        tvDetailTime = findViewById(R.id.tvDetailTime);
        tvDetailServe = findViewById(R.id.tvDetailServe);
        tvDetailDifficulty = findViewById(R.id.tvDetailDifficulty);
        layoutStepsList = findViewById(R.id.layoutStepsList);
    }

    private void loadData() {
        if (recipeId == null) return;

        db.collection("recipes").document(recipeId).get()
                .addOnSuccessListener(document -> {
                    MonAn mon = document.toObject(MonAn.class);
                    if (mon != null) {
                        tvName.setText(mon.getTenMon());
                        tvDetailTime.setText("⏱ " + mon.getThoiGian());
                        if(tvDetailServe != null) {
                            tvDetailServe.setText("👥 " + mon.getKhauPhan());
                        }
                        String doKho = mon.getDoKho();
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
                        }

                        Glide.with(this).load(mon.getHinhAnh()).into(imgDetail);

                        // Hiển thị danh sách nguyên liệu (Convert List -> String)
                        StringBuilder ingBuilder = new StringBuilder();
                        if (mon.getNguyenLieu() != null) {
                            for (String item : mon.getNguyenLieu()) {
                                ingBuilder.append("• ").append(item).append("\n");
                            }
                        }
                        tvIngredients.setText(ingBuilder.toString());

                        layoutStepsList.removeAllViews();
                        List<String> cachLams = mon.getCachLam();
                        LayoutInflater inflater = LayoutInflater.from(this);

                        if (cachLams != null) {
                            for (int i = 0; i < cachLams.size(); i++) {
                                // Inflate layout con
                                View stepView = inflater.inflate(R.layout.item_step_food, layoutStepsList, false);

                                TextView tvNum = stepView.findViewById(R.id.tvStepNumber);
                                TextView tvContent = stepView.findViewById(R.id.tvStepContent);

                                tvNum.setText(String.valueOf(i + 1));
                                tvContent.setText(cachLams.get(i));

                                layoutStepsList.addView(stepView);
                            }
                        }

                    }
                });
    }

    private void setupActions() {
        // Nút Duyệt
        btnApprove.setOnClickListener(v -> {
            Toast.makeText(this, "Đang xử lý...", Toast.LENGTH_SHORT).show();
            db.collection("recipes").document(recipeId)
                    .update("status", "approved")
                    .addOnSuccessListener(aVoid -> {
                        Toast.makeText(this, "Đã duyệt bài!", Toast.LENGTH_SHORT).show();
                        finish();
                    })
                    .addOnFailureListener(e -> Toast.makeText(this, "Lỗi: " + e.getMessage(), Toast.LENGTH_SHORT).show());
        });

        // Nút Từ chối
        btnReject.setOnClickListener(v -> {
            db.collection("recipes").document(recipeId)
                    .update("status", "rejected")
                    .addOnSuccessListener(aVoid -> {
                        Toast.makeText(this, "Đã từ chối bài viết!", Toast.LENGTH_SHORT).show();
                        finish();
                    })
                    .addOnFailureListener(e -> Toast.makeText(this, "Lỗi: " + e.getMessage(), Toast.LENGTH_SHORT).show());
        });
    }
}