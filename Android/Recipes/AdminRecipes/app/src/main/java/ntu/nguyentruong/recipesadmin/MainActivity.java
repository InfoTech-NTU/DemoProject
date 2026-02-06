package ntu.nguyentruong.recipesadmin;

import android.os.Bundle;
import android.util.Log;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.google.firebase.firestore.DocumentSnapshot;
import com.google.firebase.firestore.FirebaseFirestore;

import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {

    private RecyclerView recyclerView;
    private RecipesAdapter adapter;
    private List<MonAn> pendingList;
    private FirebaseFirestore db;
    private ImageView btnRefresh;
    private TextView tvEmptyState;
    private android.widget.ProgressBar progressBar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        EdgeToEdge.enable(this);

        db = FirebaseFirestore.getInstance();

        initViews();
        //DataSeeder.seedRecipes(this); (nạp dữ liệu)
        loadPendingRecipes();

    }

    private void initViews() {
        recyclerView = findViewById(R.id.recyclerPending);
        btnRefresh = findViewById(R.id.btnRefresh);
        tvEmptyState = findViewById(R.id.tvEmptyState);
        progressBar = findViewById(R.id.progressBar);

        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        pendingList = new ArrayList<>();
        adapter = new RecipesAdapter(this, pendingList);
        recyclerView.setAdapter(adapter);

        btnRefresh.setOnClickListener(v -> loadPendingRecipes());
    }


    private void loadPendingRecipes() {
        // 1. Khi bắt đầu tải, hiện vòng quay, ẩn list, ẩn thông báo rỗng
        progressBar.setVisibility(android.view.View.VISIBLE);
        tvEmptyState.setVisibility(android.view.View.GONE);
        recyclerView.setVisibility(android.view.View.GONE);

        db.collection("recipes")
                .whereEqualTo("status", "pending")
                .addSnapshotListener((value, error) -> {
                    // 2. Dữ liệu đã về (hoặc lỗi), tắt vòng quay ngay lập tức
                    progressBar.setVisibility(android.view.View.GONE);

                    if (error != null) {
                        Toast.makeText(this, "Lỗi kết nối!", Toast.LENGTH_SHORT).show();
                        return;
                    }

                    pendingList.clear();

                    if (value != null && !value.isEmpty()) {
                        for (DocumentSnapshot doc : value.getDocuments()) {
                            MonAn mon = doc.toObject(MonAn.class);
                            if (mon != null) {
                                mon.setId(doc.getId());
                                pendingList.add(mon);
                            }
                        }

                        recyclerView.setVisibility(android.view.View.VISIBLE);
                        tvEmptyState.setVisibility(android.view.View.GONE);

                    } else {

                        recyclerView.setVisibility(android.view.View.GONE);
                        tvEmptyState.setVisibility(android.view.View.VISIBLE);

                    }

                    adapter.notifyDataSetChanged();
                });
    }

}