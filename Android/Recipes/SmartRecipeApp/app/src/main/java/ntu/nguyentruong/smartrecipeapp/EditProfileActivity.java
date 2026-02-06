package ntu.nguyentruong.smartrecipeapp;

import android.app.ProgressDialog;
import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ImageView;
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
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.firestore.FirebaseFirestore;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class EditProfileActivity extends AppCompatActivity {

    private EditText edtFullName, edtBio, edtEmail;
    private ImageView imgAvatarEdit;
    private CardView btnChangeAvatar;
    private MaterialButton btnSave;
    private ImageButton btnBack;

    private FirebaseFirestore db;
    private FirebaseAuth mAuth;

    private Uri imageUri;
    private String currentAvatarUrl;

    // Launcher chọn ảnh
    private final ActivityResultLauncher<Intent> pickImageLauncher = registerForActivityResult(
            new ActivityResultContracts.StartActivityForResult(),
            result -> {
                if (result.getResultCode() == RESULT_OK && result.getData() != null) {
                    imageUri = result.getData().getData();
                    // Hiển thị ảnh vừa chọn lên UI
                    imgAvatarEdit.setImageURI(imageUri);
                }
            }
    );

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_edit_profile);
        initCloudinary();
        initViews();
        initFirebase();
        loadCurrentInfo();
        handleEvents();
    }

    // 1. Cấu hình Cloudinary
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

    private void initViews() {
        edtFullName = findViewById(R.id.edtFullName);
        edtBio = findViewById(R.id.edtBio);
        edtEmail = findViewById(R.id.edtEmailReadOnly);
        imgAvatarEdit = findViewById(R.id.imgAvatarEdit);
        btnChangeAvatar = findViewById(R.id.btnChangeAvatar);
        btnSave = findViewById(R.id.btnSaveProfile);
        btnBack = findViewById(R.id.btnBack);

        edtEmail.setEnabled(false);
    }

    private void initFirebase() {
        db = FirebaseFirestore.getInstance();
        mAuth = FirebaseAuth.getInstance();
    }

    private void loadCurrentInfo() {
        FirebaseUser currentUser = mAuth.getCurrentUser();
        if (currentUser == null) return;

        edtEmail.setText(currentUser.getEmail());

        db.collection("users").document(currentUser.getUid()).get()
                .addOnSuccessListener(doc -> {
                    if (doc.exists()) {
                        User user = doc.toObject(User.class);
                        if (user != null) {
                            edtFullName.setText(user.getFullName());
                            edtBio.setText(user.getBio());
                            currentAvatarUrl = user.getAvatarUrl();

                            Glide.with(this)
                                    .load(currentAvatarUrl)
                                    .placeholder(R.mipmap.ic_launcher)
                                    .circleCrop()
                                    .into(imgAvatarEdit);
                        }
                    }
                });
    }

    private void handleEvents() {
        btnBack.setOnClickListener(v -> finish());

        btnChangeAvatar.setOnClickListener(v -> {
            Intent intent = new Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
            pickImageLauncher.launch(intent);
        });

        btnSave.setOnClickListener(v -> {
            if (imageUri != null) {
                // Có chọn ảnh mới -> Nén ảnh -> Upload
                uploadImageAndSave();
            } else {
                // Không đổi ảnh -> Chỉ lưu thông tin text
                saveProfileToFirestore(currentAvatarUrl);
            }
        });
    }

    // 2. Hàm nén ảnh
    private byte[] compressImage(Uri imageUri) {
        try {
            Bitmap bitmap = MediaStore.Images.Media.getBitmap(getContentResolver(), imageUri);
            ByteArrayOutputStream stream = new ByteArrayOutputStream();
            bitmap.compress(Bitmap.CompressFormat.JPEG, 70, stream);
            return stream.toByteArray();
        } catch (IOException e) { return null; }
    }

    // 3. Upload ảnh nén lên Cloudinary
    private void uploadImageAndSave() {
        ProgressDialog progressDialog = new ProgressDialog(this);
        progressDialog.setMessage("Đang tải ảnh lên Cloudinary...");
        progressDialog.setCancelable(false);
        progressDialog.show();

        byte[] data = compressImage(imageUri);

        if (data != null) {
            MediaManager.get().upload(data)
                    .callback(new UploadCallback() {
                        @Override
                        public void onSuccess(String requestId, Map resultData) {
                            progressDialog.dismiss();
                            String newAvatarUrl = (String) resultData.get("secure_url");
                            saveProfileToFirestore(newAvatarUrl);
                        }

                        @Override
                        public void onError(String requestId, ErrorInfo errorInfo) {
                            progressDialog.dismiss();
                            Toast.makeText(EditProfileActivity.this,
                                    "Lỗi upload: " + errorInfo.getDescription(),
                                    Toast.LENGTH_LONG).show();
                        }

                        @Override public void onStart(String requestId) { }
                        @Override public void onProgress(String requestId, long bytes, long totalBytes) { }
                        @Override public void onReschedule(String requestId, ErrorInfo errorInfo) { }
                    })
                    .dispatch();
        } else {
            progressDialog.dismiss();
            Toast.makeText(this, "Lỗi xử lý ảnh", Toast.LENGTH_SHORT).show();
        }
    }

    private void saveProfileToFirestore(String avatarUrl) {
        String name = edtFullName.getText().toString().trim();
        String bio = edtBio.getText().toString().trim();
        String uid = mAuth.getUid();

        Map<String, Object> updates = new HashMap<>();
        updates.put("fullName", name);
        updates.put("bio", bio);
        if (avatarUrl != null) {
            updates.put("avatarUrl", avatarUrl);
        }

        db.collection("users").document(uid).update(updates)
                .addOnSuccessListener(aVoid -> {
                    Toast.makeText(this, "Cập nhật thành công!", Toast.LENGTH_SHORT).show();
                    setResult(RESULT_OK);
                    finish();
                })
                .addOnFailureListener(e -> Toast.makeText(this, "Lỗi Firestore: " + e.getMessage(), Toast.LENGTH_SHORT).show());
    }
}