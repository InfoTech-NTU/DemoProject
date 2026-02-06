package ntu.nguyentruong.smartrecipeapp;

import android.os.Bundle;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.firestore.QueryDocumentSnapshot;

import java.util.ArrayList;
import java.util.List;

public class FoodsActivity extends AppCompatActivity {
    private RecyclerView recyclerView;
    private ListRecipesAdapter adapter;
    private TextView tvResultCount;
    private List<MonAn> resultList = new ArrayList<>();
    private ArrayList<String> userIngredients;
    private ImageButton btnBack;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_mon_an);
        // 1. Nhận dữ liệu
        userIngredients = getIntent().getStringArrayListExtra("ingredients");
        if (userIngredients == null) userIngredients = new ArrayList<>();

        // 2. Ánh xạ View
        recyclerView = findViewById(R.id.recyclerRecipes);
        tvResultCount = findViewById(R.id.tvResultCount);
        btnBack = findViewById(R.id.btnBack);

        // 3. Setup RecyclerView
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        adapter = new ListRecipesAdapter(this, resultList, userIngredients);
        recyclerView.setAdapter(adapter);

        // 4. Xử lý nút Back
        btnBack.setOnClickListener(v -> finish());

        // 5. Gọi hàm tìm kiếm
        searchRecipes();
    }
    private void searchRecipes() {
        FirebaseFirestore db = FirebaseFirestore.getInstance();
        tvResultCount.setText("Đang tìm kiếm món ngon...");

        // Chỉ lấy những món có status là "approved"
        db.collection("recipes")
                .whereEqualTo("status", "approved")
                .get()
                .addOnSuccessListener(queryDocumentSnapshots -> {
                    resultList.clear();
                    for (QueryDocumentSnapshot doc : queryDocumentSnapshots) {
                        MonAn mon = doc.toObject(MonAn.class);
                        mon.setId(doc.getId());

                        // Logic lọc nguyên liệu giữ nguyên
                        if (isMatching(mon, userIngredients)) {
                            resultList.add(mon);
                        }
                    }
                    adapter.notifyDataSetChanged();

                    // Cập nhật text hiển thị số lượng
                    int count = resultList.size();
                    if (count > 0) {
                        tvResultCount.setText("Tìm thấy " + count + " món từ nguyên liệu của bạn");
                    } else {
                        tvResultCount.setText("Chưa tìm thấy món nào phù hợp :(");
                    }
                })
                .addOnFailureListener(e -> {
                    tvResultCount.setText("Lỗi kết nối server!");
                });
    }

    private boolean isMatching(MonAn mon, List<String> inputs) {
        if (mon.getNguyenLieu() == null) return false;
        for (String dbIng : mon.getNguyenLieu()) {
            for (String userIng : inputs) {
                if (dbIng.toLowerCase().contains(userIng.toLowerCase())) {
                    return true;
                }
            }
        }
        return false;
    }
}