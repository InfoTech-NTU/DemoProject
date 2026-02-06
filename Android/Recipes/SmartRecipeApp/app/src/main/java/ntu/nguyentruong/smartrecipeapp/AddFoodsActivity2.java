package ntu.nguyentruong.smartrecipeapp;

import android.app.ProgressDialog;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.cardview.widget.CardView;

import com.bumptech.glide.Glide;
import com.cloudinary.android.MediaManager;
import com.cloudinary.android.callback.ErrorInfo;
import com.cloudinary.android.callback.UploadCallback;
import com.google.android.material.button.MaterialButton;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.firestore.FirebaseFirestore;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class AddFoodsActivity2 extends AppCompatActivity {

    private ImageButton btnClose;
    private CardView cardUploadImage;
    private ImageView imgRealPhoto;
    private Spinner spinnerDifficulty;
    private EditText edtRecipeName, edtTime, edtServes;
    private LinearLayout layoutIngredientsContainer, layoutStepsContainer;
    private MaterialButton btnAddIngredientLine, btnAddStepLine, btnPublish;

    private Uri imageUri;
    private String oldImageUrl;
    private ActivityResultLauncher<String> imagePickerLauncher;

    private FirebaseFirestore db;
    private ProgressDialog progressDialog;

    private boolean isEditMode = false;
    private String editingRecipeId = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_add_foods2);
        db = FirebaseFirestore.getInstance();

        initViews();
        initSpinner();
        initCloudinary();
        setupImagePicker();
        handleEvents();

        // Kiểm tra Edit Mode
        if (getIntent().getBooleanExtra("IS_EDIT", false)) {
            isEditMode = true;
            editingRecipeId = getIntent().getStringExtra("RECIPE_ID");
            btnPublish.setText("Cập nhật và gửi phê duyệt");
            loadRecipeToEdit(editingRecipeId);
        } else {
            // Mặc định thêm 1 dòng trống
            addIngredientRow("");
            addStepRow("");
        }

    }

    private void initViews() {
        btnClose = findViewById(R.id.btnClose);
        cardUploadImage = findViewById(R.id.cardUploadImage);
        imgRealPhoto = findViewById(R.id.imgRealPhoto);
        edtRecipeName = findViewById(R.id.edtRecipeName);
        edtTime = findViewById(R.id.edtTime);
        edtServes = findViewById(R.id.edtServes);
        spinnerDifficulty = findViewById(R.id.spinnerDifficulty);

        layoutIngredientsContainer = findViewById(R.id.layoutIngredientsContainer);
        layoutStepsContainer = findViewById(R.id.layoutStepsContainer);

        btnAddIngredientLine = findViewById(R.id.btnAddIngredientLine);
        btnAddStepLine = findViewById(R.id.btnAddStepLine);
        btnPublish = findViewById(R.id.btnPublish);

        layoutIngredientsContainer.removeAllViews();
        layoutStepsContainer.removeAllViews();

        progressDialog = new ProgressDialog(this);
        progressDialog.setMessage("Đang xử lý dữ liệu...");
        progressDialog.setCancelable(false);
    }

    private void initSpinner() {
        String[] difficulties = {"Dễ", "Trung bình", "Khó"};
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, difficulties);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerDifficulty.setAdapter(adapter);
    }


    private void initCloudinary() {
        try {
            MediaManager.get();
        } catch (Exception e) {
            Map<String, String> config = new HashMap<>();
            config.put("cloud_name", "dcy42u29w");
            config.put("api_key", "872117492863343");
            config.put("api_secret", "3LtfxWbmmO_QD9x_Spk4sCNf4N8");
            MediaManager.init(this, config);
        }
    }

    private void setupImagePicker() {
        imagePickerLauncher = registerForActivityResult(
                new ActivityResultContracts.GetContent(),
                uri -> {
                    if (uri != null) {
                        imageUri = uri;
                        imgRealPhoto.setImageURI(uri);
                        imgRealPhoto.setVisibility(View.VISIBLE);
                        findViewById(R.id.imgRecipePreview).setVisibility(View.GONE);
                    }
                }
        );
    }

    private void handleEvents() {
        btnClose.setOnClickListener(v -> finish());
        cardUploadImage.setOnClickListener(v -> imagePickerLauncher.launch("image/*"));

        btnAddIngredientLine.setOnClickListener(v -> addIngredientRow(""));
        btnAddStepLine.setOnClickListener(v -> addStepRow(""));

        btnPublish.setOnClickListener(v -> validateAndSubmit());
    }

    // --- NGUYÊN LIỆU ---
    private void addIngredientRow(String nameVal) {
        View view = LayoutInflater.from(this).inflate(R.layout.item_add_ingredient, layoutIngredientsContainer, false);

        EditText edtName = view.findViewById(R.id.edtIngredientName);
        edtName.setText(nameVal);

        view.findViewById(R.id.btnRemove).setOnClickListener(v -> layoutIngredientsContainer.removeView(view));
        layoutIngredientsContainer.addView(view);
    }

    // --- BƯỚC LÀM ---
    private void addStepRow(String stepContent) {
        View view = LayoutInflater.from(this).inflate(R.layout.item_add_step, layoutStepsContainer, false);

        EditText edtContent = view.findViewById(R.id.edtStepContent);
        TextView tvIndex = view.findViewById(R.id.tvStepIndex);
        ImageButton btnRemove = view.findViewById(R.id.btnStepRemove);

        // Điền nội dung cũ
        edtContent.setText(stepContent);

        // Xử lý sự kiện khi bấm nút Xóa
        btnRemove.setOnClickListener(v -> {
            layoutStepsContainer.removeView(view);
        });

        layoutStepsContainer.addView(view);


    }



    // --- LOGIC VALIDATE & UPLOAD ---
    private void validateAndSubmit() {
        String name = edtRecipeName.getText().toString().trim();
        String time = edtTime.getText().toString().trim();
        String serves = edtServes.getText().toString().trim();

        if (!isEditMode && imageUri == null) {
            Toast.makeText(this, "Vui lòng chọn ảnh món ăn", Toast.LENGTH_SHORT).show();
            return;
        }

        if (name.isEmpty() || time.isEmpty() || serves.isEmpty()) {
            Toast.makeText(this, "Vui lòng nhập đủ thông tin cơ bản", Toast.LENGTH_SHORT).show();
            return;
        }

        List<String> ingredients = getIngredientsFromLayout();
        List<String> steps = getStepsFromLayout();

        if (ingredients.isEmpty() || steps.isEmpty()) {
            Toast.makeText(this, "Cần ít nhất 1 nguyên liệu và 1 bước làm", Toast.LENGTH_SHORT).show();
            return;
        }

        progressDialog.show();

        if (imageUri != null) {
            uploadToCloudinary(name, time, serves, ingredients, steps);
        } else {
            saveToFirestore(name, time, serves, ingredients, steps, oldImageUrl);
        }
    }

    private List<String> getIngredientsFromLayout() {
        List<String> list = new ArrayList<>();
        for (int i = 0; i < layoutIngredientsContainer.getChildCount(); i++) {
            View view = layoutIngredientsContainer.getChildAt(i);
            EditText edtName = view.findViewById(R.id.edtIngredientName);
            String val = edtName.getText().toString().trim();
            if (!val.isEmpty()) list.add(val);
        }
        return list;
    }

    private List<String> getStepsFromLayout() {
        List<String> list = new ArrayList<>();
        for (int i = 0; i < layoutStepsContainer.getChildCount(); i++) {
            View view = layoutStepsContainer.getChildAt(i);
            EditText edtContent = view.findViewById(R.id.edtStepContent);
            String val = edtContent.getText().toString().trim();
            if (!val.isEmpty()) list.add(val);
        }
        return list;
    }

    private void uploadToCloudinary(String name, String time, String serves, List<String> ingredients, List<String> steps) {
        byte[] data = compressImage(imageUri);
        if (data != null) {
            MediaManager.get().upload(data)
                    .callback(new UploadCallback() {
                        @Override
                        public void onSuccess(String requestId, Map resultData) {
                            String newImageUrl = (String) resultData.get("secure_url");
                            saveToFirestore(name, time, serves, ingredients, steps, newImageUrl);
                        }
                        @Override
                        public void onError(String requestId, ErrorInfo error) {
                            progressDialog.dismiss();
                            Toast.makeText(AddFoodsActivity2.this, "Lỗi upload ảnh", Toast.LENGTH_SHORT).show();
                        }
                        @Override public void onStart(String requestId) {}
                        @Override public void onReschedule(String requestId, ErrorInfo error) {}
                        @Override public void onProgress(String requestId, long bytes, long totalBytes) {}
                    }).dispatch();
        }
    }

    private void saveToFirestore(String name, String time, String serves, List<String> ingredients, List<String> steps, String imageUrl) {
        String currentUserId = FirebaseAuth.getInstance().getUid();
        db.collection("users").document(currentUserId).get()
                .addOnSuccessListener(userDoc -> {
                    String finalAuthorName = "Ẩn danh";
                    String fullName = userDoc.getString("fullName");
                    if (fullName != null && !fullName.isEmpty()) {
                        finalAuthorName = fullName;

                    }
        String difficulty = spinnerDifficulty.getSelectedItem().toString(); // Lấy độ khó

        Map<String, Object> data = new HashMap<>();
        if (isEditMode) {

        } else {
            data.put("authorId", currentUserId);
            data.put("authorName", finalAuthorName);
            data.put("createdAt", System.currentTimeMillis());
            data.put("likeCount", 0);
            data.put("likedBy", new ArrayList<String>());
        }

        // Các trường cập nhật
        data.put("tenMon", name);
        data.put("thoiGian", time);
        data.put("khauPhan", serves);
        data.put("doKho", difficulty);
        data.put("hinhAnh", imageUrl);
        data.put("nguyenLieu", ingredients);
        data.put("cachLam", steps);
        data.put("status", "pending");
        data.put("searchKeywords", generateKeywords(name));

        if (isEditMode) {
            db.collection("recipes").document(editingRecipeId).update(data)
                    .addOnSuccessListener(v -> finishPost("Cập nhật và gửi duyệt thành công."))
                    .addOnFailureListener(e -> finishPost("Lỗi: " + e.getMessage()));
        } else {
            db.collection("recipes").add(data)
                    .addOnSuccessListener(doc -> {
                        // Cập nhật lại ID
                        doc.update("id", doc.getId());
                        finishPost("Gửi thành công! Chờ duyệt nhé.");
                    })
                    .addOnFailureListener(e -> finishPost("Lỗi: " + e.getMessage()));
        }
                });
    }

    private void finishPost(String msg) {
        progressDialog.dismiss();
        Toast.makeText(this, msg, Toast.LENGTH_LONG).show();
        finish();
    }

    private void loadRecipeToEdit(String recipeId) {
        progressDialog.show();
        db.collection("recipes").document(recipeId).get()
                .addOnSuccessListener(document -> {
                    progressDialog.dismiss();
                    MonAn mon = document.toObject(MonAn.class);
                    if (mon != null) {
                        edtRecipeName.setText(mon.getTenMon());
                        edtTime.setText(mon.getThoiGian());
                        edtServes.setText(mon.getKhauPhan());
                        setSpinnerValue(mon.getDoKho());

                        oldImageUrl = mon.getHinhAnh();
                        Glide.with(this).load(oldImageUrl).into(imgRealPhoto);
                        imgRealPhoto.setVisibility(View.VISIBLE);
                        findViewById(R.id.imgRecipePreview).setVisibility(View.GONE);

                        // Load Nguyên liệu
                        if (mon.getNguyenLieu() != null) {
                            for (String item : mon.getNguyenLieu()) {
                                addIngredientRow(item);
                            }
                        }

                        // Load Steps
                        if (mon.getCachLam() != null) {
                            for (String step : mon.getCachLam()) {
                                addStepRow(step);
                            }
                        }
                    }
                })
                .addOnFailureListener(e -> progressDialog.dismiss());
    }

    private void setSpinnerValue(String value) {
        if (value == null) return;
        ArrayAdapter adapter = (ArrayAdapter) spinnerDifficulty.getAdapter();
        int position = adapter.getPosition(value);
        if (position >= 0) {
            spinnerDifficulty.setSelection(position);
        }
    }

    private List<String> generateKeywords(String name) {
        List<String> keywords = new ArrayList<>();
        String[] words = name.toLowerCase().split(" ");
        for (String word : words) keywords.add(word);
        keywords.add(name.toLowerCase());
        return keywords;
    }

    private byte[] compressImage(Uri imageUri) {
        try {
            Bitmap bitmap = MediaStore.Images.Media.getBitmap(getContentResolver(), imageUri);
            ByteArrayOutputStream stream = new ByteArrayOutputStream();
            bitmap.compress(Bitmap.CompressFormat.JPEG, 70, stream);
            return stream.toByteArray();
        } catch (IOException e) { return null; }
    }
}