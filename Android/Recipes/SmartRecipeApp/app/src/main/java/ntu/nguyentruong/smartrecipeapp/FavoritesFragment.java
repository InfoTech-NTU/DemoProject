package ntu.nguyentruong.smartrecipeapp;

import android.content.Intent;
import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import android.widget.Toast;

import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.firestore.QueryDocumentSnapshot;

import java.util.ArrayList;
import java.util.List;


public class FavoritesFragment extends Fragment {
    private RecyclerView rcvFavorites;
    private TextView tvEmptyFavorites;
    private ListRecipesAdapter favoriteAdapter;
    private List<MonAn> listYeuThich;
    List<String> emptyIngredients = new ArrayList<>();

    private FirebaseFirestore db;
    private FirebaseUser currentUser;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        return inflater.inflate(R.layout.fragment_favorites, container, false);
    }
    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        // 1. Khởi tạo Firebase
        db = FirebaseFirestore.getInstance();
        currentUser = FirebaseAuth.getInstance().getCurrentUser();

        // 2. Ánh xạ View
        rcvFavorites = view.findViewById(R.id.recyclerFavorites);
        tvEmptyFavorites = view.findViewById(R.id.tvEmptyFavorites);

        // 3. Setup RecyclerView
        listYeuThich = new ArrayList<>();

        favoriteAdapter = new ListRecipesAdapter(getContext(), listYeuThich, emptyIngredients);

        LinearLayoutManager linearLayoutManager = new LinearLayoutManager(getContext());
        rcvFavorites.setLayoutManager(linearLayoutManager);
        rcvFavorites.setAdapter(favoriteAdapter);
    }

    // Dùng onResume để load lại danh sách mỗi khi quay lại tab này
    @Override
    public void onResume() {
        super.onResume();
        loadFavoriteRecipes();
    }

    private void loadFavoriteRecipes() {
        String currentUserId = currentUser.getUid();

        db.collection("recipes")
                .whereArrayContains("likedBy", currentUserId)
                .get()
                .addOnSuccessListener(queryDocumentSnapshots -> {
                    listYeuThich.clear(); // Xóa dữ liệu cũ

                    for (QueryDocumentSnapshot doc : queryDocumentSnapshots) {
                        MonAn monAn = doc.toObject(MonAn.class);
                        monAn.setId(doc.getId());
                        listYeuThich.add(monAn);
                    }

                    // Cập nhật giao diện
                    favoriteAdapter.notifyDataSetChanged();

                    if (listYeuThich.isEmpty()) {
                        tvEmptyFavorites.setVisibility(View.VISIBLE);
                        rcvFavorites.setVisibility(View.GONE);
                    } else {
                        tvEmptyFavorites.setVisibility(View.GONE);
                        rcvFavorites.setVisibility(View.VISIBLE);
                    }
                })
                .addOnFailureListener(e -> {
                    if (getContext() != null) {
                        Toast.makeText(getContext(), "Lỗi: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }
}