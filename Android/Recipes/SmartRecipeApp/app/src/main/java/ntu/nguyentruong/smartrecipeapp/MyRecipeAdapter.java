package ntu.nguyentruong.smartrecipeapp;

import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;
import com.google.firebase.firestore.FirebaseFirestore;

import java.util.List;

public class MyRecipeAdapter extends RecyclerView.Adapter<MyRecipeAdapter.MyRecipeViewHolder> {

    private Context context;
    private List<MonAn> monAnList;

    public MyRecipeAdapter(Context context, List<MonAn> monAnList) {
        this.context = context;
        this.monAnList = monAnList;
    }

    @NonNull
    @Override
    public MyRecipeViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.item_mini, parent, false);
        return new MyRecipeViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull MyRecipeViewHolder holder, int position) {
        MonAn monAn = monAnList.get(position);

        // 1. Hiển thị thông tin cơ bản
        holder.tvFoodName.setText(monAn.getTenMon());
        Glide.with(context)
                .load(monAn.getHinhAnh())
                .placeholder(R.mipmap.ic_launcher)
                .error(R.mipmap.ic_launcher)
                .into(holder.imgFood);

        // 2. Hiển thị trạng thái (Màu sắc)
        String status = monAn.getStatus();
        if (status == null) status = "approved";

        switch (status) {
            case "pending":
                holder.tvStatus.setText("• Đang chờ duyệt");
                holder.tvStatus.setTextColor(Color.parseColor("#FFA500"));
                break;
            case "rejected":
                holder.tvStatus.setText("• Bị từ chối");
                holder.tvStatus.setTextColor(Color.parseColor("#FF0000"));
                break;
            case "approved":
                holder.tvStatus.setText("• Đã đăng");
                holder.tvStatus.setTextColor(Color.parseColor("#4CAF50"));
                break;
        }

        // --- CÁC SỰ KIỆN CLICK ---

        // A. Nhấn vào cả dòng -> Xem chi tiết (DetailActivity)
        holder.itemView.setOnClickListener(v -> {
            Intent intent = new Intent(context, DetailActivity.class);
            // Gửi dữ liệu sang trang chi tiết
            intent.putExtra("object_monan", monAn);
            context.startActivity(intent);
        });

        // B. Nhấn nút Sửa -> Vào AddFoodsActivity2
        holder.btnEdit.setOnClickListener(v -> {
            Intent intent = new Intent(context, AddFoodsActivity2.class);
            intent.putExtra("RECIPE_ID", monAn.getId());
            intent.putExtra("IS_EDIT", true); // Báo hiệu là sửa
            context.startActivity(intent);
        });

        // C. Nhấn nút Xóa -> Hiện hộp thoại xác nhận
        holder.btnDelete.setOnClickListener(v -> {
            new AlertDialog.Builder(context)
                    .setTitle("Xác nhận xóa")
                    .setMessage("Bạn có chắc chắn muốn xóa bài viết '" + monAn.getTenMon() + "' không?")
                    .setPositiveButton("Xóa", (dialog, which) -> {
                        deleteRecipe(monAn.getId());
                    })
                    .setNegativeButton("Hủy", null)
                    .show();
        });
        holder.tvLikeCount.setText(monAn.getLikeCount() + " ❤️");

        if (holder.layoutActionButtons != null) {
            holder.layoutActionButtons.setVisibility(View.VISIBLE);
        }
    }

    // Hàm xóa bài viết trên Firebase
    private void deleteRecipe(String recipeId) {
        FirebaseFirestore.getInstance().collection("recipes")
                .document(recipeId)
                .delete()
                .addOnSuccessListener(aVoid -> {
                    Toast.makeText(context, "Đã xóa bài viết!", Toast.LENGTH_SHORT).show();
                    // List sẽ tự cập nhật nhờ snapshotListener bên Activity, không cần remove tay ở đây
                })
                .addOnFailureListener(e -> {
                    Toast.makeText(context, "Lỗi khi xóa: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                });
    }

    @Override
    public int getItemCount() {
        return monAnList.size();
    }

    public static class MyRecipeViewHolder extends RecyclerView.ViewHolder {
        ImageView imgFood;
        TextView tvFoodName, tvStatus,tvLikeCount;
        ImageButton btnEdit, btnDelete;
        LinearLayout layoutActionButtons;

        public MyRecipeViewHolder(@NonNull View itemView) {
            super(itemView);
            imgFood = itemView.findViewById(R.id.imgFood);
            tvFoodName = itemView.findViewById(R.id.tvFoodName);
            tvStatus = itemView.findViewById(R.id.tvStatus);
            tvLikeCount = itemView.findViewById(R.id.tvLikeCount);
            btnEdit = itemView.findViewById(R.id.btnEdit);
            btnDelete = itemView.findViewById(R.id.btnDelete);
            layoutActionButtons = itemView.findViewById(R.id.layoutActionButtons);
        }
    }
}