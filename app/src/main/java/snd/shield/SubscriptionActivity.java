package snd.shield;

import android.os.Bundle;
import android.view.View;
import android.view.animation.OvershootInterpolator;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import snd.shield.util.Nav;
import snd.shield.util.NeoAnim;

public class SubscriptionActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_subscription);

        View header = findViewById(R.id.header);
        ((TextView) header.findViewById(R.id.headerTitle))
                .setText(R.string.tool_subscription);
        View back = header.findViewById(R.id.btnBack);
        NeoAnim.attachPress(back);
        back.setOnClickListener(v -> Nav.back(this));
        NeoAnim.attachPress(header.findViewById(R.id.btnAction));

        // Crown bounce
        View crown = findViewById(R.id.crownBg);
        crown.setScaleX(0.5f); crown.setScaleY(0.5f); crown.setAlpha(0f);
        crown.animate().scaleX(1f).scaleY(1f).alpha(1f)
                .setInterpolator(new OvershootInterpolator(2.4f))
                .setDuration(560).start();

        // Plan press feedback
        NeoAnim.attachPress(findViewById(R.id.planFree));
        NeoAnim.attachPress(findViewById(R.id.planPremium));
        NeoAnim.attachPress(findViewById(R.id.planLifetime));

        bindCta(R.id.btnFreePick, "Already on free plan");
        bindCta(R.id.btnPremiumPick, "Premium checkout flow");
        bindCta(R.id.btnLifetimePick, "Lifetime checkout flow");
    }

    private void bindCta(int id, String msg) {
        View v = findViewById(id);
        if (v == null) return;
        NeoAnim.attachPress(v);
        v.setOnClickListener(b -> Toast.makeText(this, msg, Toast.LENGTH_SHORT).show());
    }

    @Override
    public void onBackPressed() { Nav.back(this); }
}
