package snd.shield;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.animation.AnimationUtils;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import java.util.ArrayList;
import java.util.List;

import snd.shield.util.Nav;
import snd.shield.util.NeoAnim;

public class ManageUsersActivity extends AppCompatActivity {

    static class User {
        String name, email, role;
        boolean blocked;
        User(String n, String e, String r, boolean b) {
            name = n; email = e; role = r; blocked = b;
        }
    }

    private final List<User> users = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_manage_users);

        View header = findViewById(R.id.header);
        ((TextView) header.findViewById(R.id.headerTitle))
                .setText(R.string.tool_manage_users);
        View back = header.findViewById(R.id.btnBack);
        NeoAnim.attachPress(back);
        back.setOnClickListener(v -> Nav.back(this));
        NeoAnim.attachPress(header.findViewById(R.id.btnAction));

        seedUsers();

        // Stats
        int total = users.size();
        int premium = 0; int blocked = 0;
        for (User u : users) {
            if ("Premium".equals(u.role)) premium++;
            if (u.blocked) blocked++;
        }
        NeoAnim.countUp(findViewById(R.id.usrTotal), 0, total, 800);
        NeoAnim.countUp(findViewById(R.id.usrPremium), 0, premium, 800);
        NeoAnim.countUp(findViewById(R.id.usrBlocked), 0, blocked, 800);

        // Buttons
        View btnAdd = findViewById(R.id.btnAdd);
        NeoAnim.attachPress(btnAdd);
        btnAdd.setOnClickListener(v ->
                Toast.makeText(this, "Open invite user form",
                        Toast.LENGTH_SHORT).show());

        View btnBroadcast = findViewById(R.id.btnBroadcast);
        NeoAnim.attachPress(btnBroadcast);
        btnBroadcast.setOnClickListener(v ->
                Toast.makeText(this, "Compose broadcast message",
                        Toast.LENGTH_SHORT).show());

        // List
        RecyclerView list = findViewById(R.id.usersList);
        list.setLayoutManager(new LinearLayoutManager(this));
        list.setAdapter(new UserAdapter());
        list.setLayoutAnimation(AnimationUtils.loadLayoutAnimation(
                this, R.anim.list_layout_anim));
    }

    private void seedUsers() {
        users.add(new User("Akash Molla", "akash@example.com", "Premium", false));
        users.add(new User("Tania Khan", "tania@example.com", "Free", false));
        users.add(new User("Rahim Uddin", "rahim@example.com", "Free", false));
        users.add(new User("Sumi Akter", "sumi@example.com", "Premium", false));
        users.add(new User("Spam Bot", "bot42@spam.io", "Free", true));
        users.add(new User("Karim Ali", "karim@example.com", "Free", false));
        users.add(new User("Nadia Hossain", "nadia@example.com", "Premium", false));
    }

    private class UserAdapter extends RecyclerView.Adapter<UserAdapter.VH> {
        @NonNull @Override
        public VH onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            return new VH(LayoutInflater.from(parent.getContext())
                    .inflate(R.layout.item_user_row, parent, false));
        }

        @Override
        public void onBindViewHolder(@NonNull VH h, int pos) {
            User u = users.get(pos);
            h.name.setText(u.name);
            h.email.setText(u.email);
            h.role.setText(u.blocked ? "Blocked" : u.role);
            h.initials.setText(u.name.isEmpty() ? "?"
                    : String.valueOf(u.name.charAt(0)).toUpperCase());
            NeoAnim.attachPress(h.itemView);
            NeoAnim.attachPress(h.more);
            h.more.setOnClickListener(v ->
                    Toast.makeText(ManageUsersActivity.this,
                            "Manage " + u.name, Toast.LENGTH_SHORT).show());
        }

        @Override public int getItemCount() { return users.size(); }

        class VH extends RecyclerView.ViewHolder {
            TextView name, email, role, initials;
            View more;
            VH(@NonNull View v) {
                super(v);
                name = v.findViewById(R.id.userName);
                email = v.findViewById(R.id.userEmail);
                role = v.findViewById(R.id.userRole);
                initials = v.findViewById(R.id.userInitials);
                more = v.findViewById(R.id.userMore);
            }
        }
    }

    @Override
    public void onBackPressed() { Nav.back(this); }
}
