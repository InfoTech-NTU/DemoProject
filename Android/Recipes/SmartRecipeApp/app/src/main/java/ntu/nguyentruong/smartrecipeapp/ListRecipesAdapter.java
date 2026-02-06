package ntu.nguyentruong.smartrecipeapp;

import android.content.Context;
import android.content.Intent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;

import java.util.ArrayList;
import java.util.List;

public class ListRecipesAdapter extends RecyclerView.Adapter<ListRecipesAdapter.ItemRecipesViewHolder>
{
    private Context context;
    private List<MonAn> listMonAn;
    private List<String> userIngredients;

    public ListRecipesAdapter(Context context, List<MonAn> listMonAn, List<String> userIngredients) {
        this.context = context;
        this.listMonAn = listMonAn;
        this.userIngredients = userIngredients;
    }

    @NonNull
    @Override
    public ItemRecipesViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        LayoutInflater inflater = LayoutInflater.from(context);
        View view = inflater.inflate(R.layout.item_monan, parent, false);
        return new ItemRecipesViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ItemRecipesViewHolder holder, int position) {
        MonAn mon = listMonAn.get(position);

        holder.tvName.setText(mon.getTenMon());
        holder.tvTime.setText(mon.getThoiGian());
        holder.tvDifficulty.setText(mon.getDoKho());
        holder.tvlikeCount.setText(mon.getLikeCount() +  " ❤️");

        Glide.with(context).load(mon.getHinhAnh()).into(holder.imgFood);

        List<String> missingItems = new ArrayList<>();
        if (mon.getNguyenLieu() != null && userIngredients != null) {
            for (String recipeIng : mon.getNguyenLieu()) {
                boolean haveIt = false;
                for (String userIng : userIngredients) {
                    // So sánh tương đối (vd: "thịt" khớp "thịt gà")
                    if (recipeIng.toLowerCase().contains(userIng.toLowerCase()) ||
                            userIng.toLowerCase().contains(recipeIng.toLowerCase())) {
                        haveIt = true;
                        break;
                    }
                }
                if (!haveIt) {
                    missingItems.add(recipeIng);
                }
            }
        }

        holder.itemView.setOnClickListener(view -> {
            MonAn monAnClick = listMonAn.get(position);

            Intent intent = new Intent(context, DetailActivity.class);
            // Truyền cả object MonAn sang
            intent.putExtra("object_monan", monAnClick);
            context.startActivity(intent);
        });
        if (missingItems.isEmpty()) {
            holder.tvMissing.setText("Đủ nguyên liệu! Nấu ngay!");
            holder.tvMissing.setTextColor(context.getResources().getColor(android.R.color.holo_green_dark));
            holder.tvMissing.setBackgroundColor(0x154CAF50);
        } else {
            String text = "Thiếu: " + String.join(", ", missingItems);
            holder.tvMissing.setText(text);
        }
    }

    @Override
    public int getItemCount() {
        return listMonAn.size();
    }

    public static class ItemRecipesViewHolder extends RecyclerView.ViewHolder {
        ImageView imgFood;
        TextView tvName, tvTime, tvDifficulty, tvMissing,tvlikeCount;
        ImageButton btnFavorite;


        public ItemRecipesViewHolder(@NonNull View itemView) {
            super(itemView);
            imgFood = itemView.findViewById(R.id.imgFood);
            tvName = itemView.findViewById(R.id.tvRecipeName);
            tvTime = itemView.findViewById(R.id.tvTime);
            tvDifficulty = itemView.findViewById(R.id.tvDifficulty);
            tvMissing = itemView.findViewById(R.id.tvMissingIngredients);
            btnFavorite = itemView.findViewById(R.id.btnFavorite);
            tvlikeCount = itemView.findViewById(R.id.tvLikeCount);
        }
    }
}
