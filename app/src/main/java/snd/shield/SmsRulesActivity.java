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
import androidx.appcompat.widget.SwitchCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import java.util.ArrayList;
import java.util.List;

import snd.shield.util.Nav;
import snd.shield.util.NeoAnim;

public class SmsRulesActivity extends AppCompatActivity {

    static class Rule {
        String title; String subtitle; boolean enabled; boolean isBlock;
        Rule(String t, String s, boolean e, boolean b) {
            title = t; subtitle = s; enabled = e; isBlock = b;
        }
    }

    private final List<Rule> all = new ArrayList<>();
    private RuleAdapter adapter;
    private boolean blockMode = true;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_sms_rules);

        // Header
        View header = findViewById(R.id.header);
        ((TextView) header.findViewById(R.id.headerTitle))
                .setText(R.string.tool_sms_rules);
        View back = header.findViewById(R.id.btnBack);
        NeoAnim.attachPress(back);
        back.setOnClickListener(v -> Nav.back(this));
        NeoAnim.attachPress(header.findViewById(R.id.btnAction));

        // Seed sample
        all.add(new Rule("+8801711000000", "Repeat sender — auto blocked", true, true));
        all.add(new Rule("+8801999888777", "Reported as spam", true, true));
        all.add(new Rule("VK-OFFER", "Promotional sender ID", false, true));
        all.add(new Rule("MyBank", "Allow OTP banking sender", true, false));
        all.add(new Rule("FB-OTP", "Allow Facebook OTP", true, false));

        adapter = new RuleAdapter();
        RecyclerView list = findViewById(R.id.rulesList);
        list.setLayoutManager(new LinearLayoutManager(this));
        list.setAdapter(adapter);
        list.setLayoutAnimation(AnimationUtils.loadLayoutAnimation(
                this, R.anim.list_layout_anim));

        // Segmented control
        TextView segBlock = findViewById(R.id.segBlock);
        TextView segAllow = findViewById(R.id.segAllow);
        View indicator = findViewById(R.id.segIndicator);
        NeoAnim.attachPress(segBlock);
        NeoAnim.attachPress(segAllow);
        segBlock.post(() -> indicator.getLayoutParams().width = segBlock.getWidth());
        segBlock.setOnClickListener(v -> setMode(true, indicator, segBlock, segAllow));
        segAllow.setOnClickListener(v -> setMode(false, indicator, segBlock, segAllow));

        // Add
        View btnAdd = findViewById(R.id.btnAdd);
        NeoAnim.attachPress(btnAdd);
        btnAdd.setOnClickListener(v -> {
            all.add(0, new Rule("New rule", "Tap to edit", true, blockMode));
            adapter.notifyItemInserted(0);
            list.smoothScrollToPosition(0);
            Toast.makeText(this, "Rule added", Toast.LENGTH_SHORT).show();
        });

        adapter.refresh();
    }

    private void setMode(boolean block, View indicator, TextView segBlock, TextView segAllow) {
        if (block == blockMode) return;
        blockMode = block;
        float dx = block ? 0f : segBlock.getWidth();
        indicator.animate().translationX(dx).setDuration(220).start();
        segBlock.setTextColor(getResources().getColor(
                block ? R.color.text_on_brand : R.color.text_secondary));
        segAllow.setTextColor(getResources().getColor(
                block ? R.color.text_secondary : R.color.text_on_brand));
        adapter.refresh();
    }

    private class RuleAdapter extends RecyclerView.Adapter<RuleAdapter.VH> {
        private List<Rule> filtered = new ArrayList<>();

        void refresh() {
            filtered.clear();
            for (Rule r : all) {
                if (r.isBlock == blockMode) filtered.add(r);
            }
            notifyDataSetChanged();
        }

        @NonNull @Override
        public VH onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            View v = LayoutInflater.from(parent.getContext())
                    .inflate(R.layout.item_rule_row, parent, false);
            return new VH(v);
        }

        @Override
        public void onBindViewHolder(@NonNull VH h, int pos) {
            Rule r = filtered.get(pos);
            h.title.setText(r.title);
            h.subtitle.setText(r.subtitle);
            h.toggle.setChecked(r.enabled);
            h.toggle.setOnCheckedChangeListener((b, isOn) -> r.enabled = isOn);
            NeoAnim.attachPress(h.itemView);
        }

        @Override public int getItemCount() { return filtered.size(); }

        class VH extends RecyclerView.ViewHolder {
            TextView title, subtitle;
            SwitchCompat toggle;
            VH(@NonNull View v) {
                super(v);
                title = v.findViewById(R.id.ruleTitle);
                subtitle = v.findViewById(R.id.ruleSubtitle);
                toggle = v.findViewById(R.id.ruleSwitch);
            }
        }
    }

    @Override
    public void onBackPressed() { Nav.back(this); }
}
