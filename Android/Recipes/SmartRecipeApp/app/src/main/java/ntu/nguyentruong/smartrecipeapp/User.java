package ntu.nguyentruong.smartrecipeapp;

import java.io.Serializable;

public class User implements Serializable {
    private String uid;
    private String email;
    private String fullName;
    private String avatarUrl;
    private String bio;

    public User() { }

    public User(String uid, String email, String fullName, String avatarUrl, String bio) {
        this.uid = uid;
        this.email = email;
        this.fullName = fullName;
        this.avatarUrl = avatarUrl;
        this.bio = bio;
    }

    public String getUid() { return uid; }
    public void setUid(String uid) { this.uid = uid; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getFullName() { return fullName; }
    public void setFullName(String fullName) { this.fullName = fullName; }

    public String getAvatarUrl() { return avatarUrl; }
    public void setAvatarUrl(String avatarUrl) { this.avatarUrl = avatarUrl; }
    public String getBio() { return bio; }
    public void setBio(String bio) { this.bio = bio; }
}
