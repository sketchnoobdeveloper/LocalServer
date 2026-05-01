package snd.shield;

import android.graphics.Color;
import android.graphics.PorterDuff;
import android.graphics.drawable.GradientDrawable;
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

public class RequestManagerActivity extends AppCompatActivity {

    static class Endpoint {
        String method, path, meta;
        int statusColor;
        Endpoint(String m, String p, String d, int c) {
            method = m; path = p; meta = d; statusColor = c;
        }
    }

    private final List<Endpoint> endpoints = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_request_manager);

        View header = findViewById(R.id.header);
        ((TextView) header.findViewById(R.id.headerTitle))
                .setText(R.string.tool_request_manager);
        View back = header.findViewById(R.id.btnBack);
        NeoAnim.attachPress(back);
        back.setOnClickListener(v -> Nav.back(this));
        NeoAnim.attachPress(header.findViewById(R.id.btnAction));

        // Stats
        NeoAnim.countUp(findViewById(R.id.apiEndpoints), 0, 18, 800);
        NeoAnim.countUp(findViewById(R.id.apiCalls), 0, 1247, 1000);
        NeoAnim.countUp(findViewById(R.id.apiErrors), 0, 12, 700);

        View btnAdd = findViewById(R.id.btnAdd);
        NeoAnim.attachPress(btnAdd);
        btnAdd.setOnClickListener(v ->
                Toast.makeText(this, "Add new endpoint",
                        Toast.LENGTH_SHORT).show());

        seedEndpoints();
        RecyclerView list = findViewById(R.id.apiList);
        list.setLayoutManager(new LinearLayoutManager(this));
        list.setAdapter(new ApiAdapter());
        list.setLayoutAnimation(AnimationUtils.loadLayoutAnimation(
                this, R.anim.list_layout_anim));
    }

    private void seedEndpoints() {
        endpoints.add(new Endpoint("GET", "/api/v1/scan/sms",
                "200 OK \u00B7 184 ms \u00B7 today 12:30",
                Color.parseColor("#3D5AFE")));
        endpoints.add(new Endpoint("POST", "/api/v1/rule",
                "201 Created \u00B7 92 ms \u00B7 today 12:18",
                Color.parseColor("#16C784")));
        endpoints.add(new Endpoint("PUT", "/api/v1/user/role",
                "200 OK \u00B7 110 ms \u00B7 today 11:50",
                Color.parseColor("#FFB020")));
        endpoints.add(new Endpoint("DELETE", "/api/v1/rule/42",
                "204 No Content \u00B7 78 ms \u00B7 today 11:00",
                Color.parseColor("#FF4D6D")));
        endpoints.add(new Endpoint("GET", "/api/v1/protection/score",
                "200 OK \u00B7 64 ms \u00B7 today 10:42",
                Color.parseColor("#3D5AFE")));
        endpoints.add(new Endpoint("POST", "/api/v1/report/whatsapp",
                "200 OK \u00B7 240 ms \u00B7 today 09:30",
                Color.parseColor("#16C784")));
    }

    private class ApiAdapter extends RecyclerView.Adapter<ApiAdapter.VH> {
        @NonNull @Override
        public VH onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            return new VH(LayoutInflater.from(parent.getContext())
                    .inflate(R.layout.item_api_row, parent, false));
        }

        @Override
        public void onBindViewHolder(@NonNull VH h, int pos) {
            Endpoint e = endpoints.get(pos);
            h.method.setText(e.method);
            h.path.setText(e.path);
            h.meta.setText(e.meta);
            h.method.getBackground().setColorFilter(
                    e.statusColor, PorterDuff.Mode.SRC_IN);
            NeoAnim.attachPress(h.itemView);
            NeoAnim.attachPress(h.more);
            h.itemView.setOnClickListener(v ->
                    Toast.makeText(RequestManagerActivity.this,
                            e.method + " " + e.path,
                            Toast.LENGTH_SHORT).show());
        }

        @Override public int getItemCount() { return endpoints.size(); }

        class VH extends RecyclerView.ViewHolder {
            TextView method, path, meta;
            View more;
            VH(@NonNull View v) {
                super(v);
                method = v.findViewById(R.id.apiMethod);
                path = v.findViewById(R.id.apiPath);
                meta = v.findViewById(R.id.apiMeta);
                more = v.findViewById(R.id.apiMore);
            }
        }
    }

    @Override
    public void onBackPressed() { Nav.back(this); }
}
