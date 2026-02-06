package ntu.nguyentruong.smartrecipeapp;

import android.content.Intent;
import android.os.Bundle;

import androidx.fragment.app.Fragment;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AutoCompleteTextView;

import com.google.android.material.button.MaterialButton;
import com.google.android.material.chip.Chip;
import com.google.android.material.chip.ChipGroup;
import com.google.android.material.floatingactionbutton.FloatingActionButton;

import java.util.ArrayList;

public class FridgeFragment extends Fragment {
    private AutoCompleteTextView edtNguyenLieu;
    private FloatingActionButton btnAdd;
    private ChipGroup chipGroup;
    private MaterialButton btnSearch;
    private ArrayList<String> myIngredients = new ArrayList<>();

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState)
    {
        View view = inflater.inflate(R.layout.fragment_fridge, container, false);
        edtNguyenLieu = view.findViewById(R.id.edtNguyenLieu);
        btnAdd = view.findViewById(R.id.btnAddIngredient);
        chipGroup = view.findViewById(R.id.chipGroupNguyenLieu);
        btnSearch = view.findViewById(R.id.btnSearchCongThuc);
        // Xóa tất cả các Chip cũ
        chipGroup.removeAllViews();

        // 1. Sự kiện nút Thêm (+)
        btnAdd.setOnClickListener(v -> {
            String text = edtNguyenLieu.getText().toString().trim();
            if (!text.isEmpty()) {
                addChip(text);
                edtNguyenLieu.setText("");
            }
        });

        // 2. Sự kiện nút "Nấu thôi!"
        btnSearch.setOnClickListener(v -> {
            // Chuyển sang màn hình kết quả, gửi kèm danh sách nguyên liệu
            Intent intent = new Intent(getContext(), FoodsActivity.class);
            intent.putStringArrayListExtra("ingredients", myIngredients);
            startActivity(intent);
        });

        return view;
    }
    private void addChip(String text) {
        myIngredients.add(text);

        // Tạo Chip giao diện
        Chip chip = new Chip(getContext());
        chip.setText(text);
        chip.setCloseIconVisible(true);
        chip.setCheckable(false);
        // Style cho giống XML của bạn
        chip.setChipBackgroundColorResource(R.color.pink_light);

        // Sự kiện xóa chip
        chip.setOnCloseIconClickListener(v -> {
            chipGroup.removeView(chip);
            myIngredients.remove(text);
        });

        chipGroup.addView(chip);
    }
}