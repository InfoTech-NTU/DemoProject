package ntu.nguyentruong.recipesadmin;

import android.content.Context;
import android.content.Intent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;

import java.util.List;

public class RecipesAdapter extends RecyclerView.Adapter<RecipesAdapter.ItemRecipesViewHolder> {

    private Context context;
    private List<MonAn> list;

    public RecipesAdapter(Context context, List<MonAn> list) {
        this.context = context;
        this.list = list;
    }

    @NonNull
    @Override
    public ItemRecipesViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.item_admin_recipe, parent, false);
        return new ItemRecipesViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ItemRecipesViewHolder holder, int position) {
        MonAn mon = list.get(position);

        holder.tvName.setText(mon.getTenMon());
        holder.tvInfo.setText(mon.getAuthorName());

        Glide.with(context)
                .load(mon.getHinhAnh())
                .placeholder(R.mipmap.ic_launcher)
                .into(holder.imgThumb);

        // Click vào item -> Mở trang duyệt
        holder.itemView.setOnClickListener(v -> {
            Intent intent = new Intent(context, DetailRecipesActivity.class);
            intent.putExtra("RECIPE_ID", mon.getId()); // Truyền ID
            context.startActivity(intent);
        });
    }

    @Override
    public int getItemCount() {
        return list.size();
    }

    public static class ItemRecipesViewHolder extends RecyclerView.ViewHolder {
        ImageView imgThumb;
        TextView tvName, tvInfo;

        public ItemRecipesViewHolder(@NonNull View itemView) {
            super(itemView);
            imgThumb = itemView.findViewById(R.id.imgFoodThumb);
            tvName = itemView.findViewById(R.id.tvFoodName);
            tvInfo = itemView.findViewById(R.id.tvAuthorTime);

        }
    }
}
