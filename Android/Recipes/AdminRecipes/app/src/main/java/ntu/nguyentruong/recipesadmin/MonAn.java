package ntu.nguyentruong.recipesadmin;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

public class MonAn implements Serializable {
    private String id;              // ID document trên Firestore
    private String tenMon;
    private String hinhAnh;         // URL ảnh
    private String thoiGian;
    private String khauPhan;
    private String doKho;
    private List<String> nguyenLieu;
    private List<String> cachLam;
    private String authorId;        // UID người đăng
    private String authorName;      // Tên người đăng
    private String status;          // "pending" (chờ), "approved" (duyệt), "rejected" (hủy)
    private int likeCount;          // Số lượt thích
    private List<String> likedBy;// Danh sách UID những người đã like
    private long createdAt;

    public MonAn() {}

    public MonAn(String id, String tenMon, String hinhAnh, String thoiGian, String khauPhan, String doKho, List<String> nguyenLieu, List<String> cachLam, String authorId, String authorName, String status, int likeCount, List<String> likedBy, long createdAt) {
        this.id = id;
        this.tenMon = tenMon;
        this.hinhAnh = hinhAnh;
        this.thoiGian = thoiGian;
        this.khauPhan = khauPhan;
        this.doKho = doKho;
        this.nguyenLieu = nguyenLieu;
        this.cachLam = cachLam;
        this.authorId = authorId;
        this.authorName = authorName;
        this.status = status;
        this.likeCount = likeCount;
        this.likedBy = likedBy;
        this.createdAt = createdAt;
    }

    public MonAn(String id, String tenMon, String hinhAnh, String thoiGian, String khauPhan, String doKho, List<String> nguyenLieu, List<String> cachLam, String authorId, String authorName, String status, int likeCount, List<String> likedBy) {
        this.id = id;
        this.tenMon = tenMon;
        this.hinhAnh = hinhAnh;
        this.thoiGian = thoiGian;
        this.khauPhan = khauPhan;
        this.doKho = doKho;
        this.nguyenLieu = nguyenLieu;
        this.cachLam = cachLam;
        this.authorId = authorId;
        this.authorName = authorName;
        this.status = "pending";
        this.likeCount = 0;
        this.likedBy = new ArrayList<>();
        this.createdAt = System.currentTimeMillis();
    }

    public long getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(long createdAt) {
        this.createdAt = createdAt;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getTenMon() {
        return tenMon;
    }

    public void setTenMon(String tenMon) {
        this.tenMon = tenMon;
    }

    public String getHinhAnh() {
        return hinhAnh;
    }

    public void setHinhAnh(String hinhAnh) {
        this.hinhAnh = hinhAnh;
    }

    public String getThoiGian() {
        return thoiGian;
    }

    public void setThoiGian(String thoiGian) {
        this.thoiGian = thoiGian;
    }

    public String getKhauPhan() {
        return khauPhan;
    }

    public void setKhauPhan(String khauPhan) {
        this.khauPhan = khauPhan;
    }

    public String getDoKho() {
        return doKho;
    }

    public void setDoKho(String doKho) {
        this.doKho = doKho;
    }

    public List<String> getNguyenLieu() {
        return nguyenLieu;
    }

    public void setNguyenLieu(List<String> nguyenLieu) {
        this.nguyenLieu = nguyenLieu;
    }

    public List<String> getCachLam() {
        return cachLam;
    }

    public void setCachLam(List<String> cachLam) {
        this.cachLam = cachLam;
    }

    public String getAuthorId() {
        return authorId;
    }

    public void setAuthorId(String authorId) {
        this.authorId = authorId;
    }

    public String getAuthorName() {
        return authorName;
    }

    public void setAuthorName(String authorName) {
        this.authorName = authorName;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public int getLikeCount() {
        return likeCount;
    }

    public void setLikeCount(int likeCount) {
        this.likeCount = likeCount;
    }

    public List<String> getLikedBy() {
        return likedBy;
    }

    public void setLikedBy(List<String> likedBy) {
        this.likedBy = likedBy;
    }
}
