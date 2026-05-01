package snd.shield;

import android.os.Bundle;
import android.view.View;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import snd.shield.util.Nav;
import snd.shield.util.NeoAnim;

public class MyProtectionActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_my_protection);

        View header = findViewById(R.id.header);
        ((TextView) header.findViewById(R.id.headerTitle))
                .setText(R.string.tool_my_protection);
        View back = header.findViewById(R.id.btnBack);
        NeoAnim.attachPress(back);
        back.setOnClickListener(v -> Nav.back(this));
        NeoAnim.attachPress(header.findViewById(R.id.btnAction));

        // Score animation
        NeoAnim.countUp(findViewById(R.id.scoreValue), 0, 92, 1100);
        View ring = findViewById(R.id.scoreRing);
        ring.setScaleX(0.8f); ring.setScaleY(0.8f); ring.setAlpha(0f);
        ring.animate().scaleX(1f).scaleY(1f).alpha(1f)
                .setDuration(560).start();

        NeoAnim.enterScreen(findViewById(android.R.id.content));
    }

    @Override
    public void onBackPressed() { Nav.back(this); }
}
