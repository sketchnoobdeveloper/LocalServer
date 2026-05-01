package snd.shield;

import android.os.Bundle;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import snd.shield.util.Nav;
import snd.shield.util.NeoAnim;

public class MultiChannelGuardActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_multi_channel_guard);

        View header = findViewById(R.id.header);
        ((TextView) header.findViewById(R.id.headerTitle))
                .setText(R.string.tool_multi_guard);
        View back = header.findViewById(R.id.btnBack);
        NeoAnim.attachPress(back);
        back.setOnClickListener(v -> Nav.back(this));
        NeoAnim.attachPress(header.findViewById(R.id.btnAction));

        NeoAnim.attachPress(findViewById(R.id.rowSms));
        NeoAnim.attachPress(findViewById(R.id.rowCall));
        NeoAnim.attachPress(findViewById(R.id.rowEmail));
        NeoAnim.attachPress(findViewById(R.id.rowWhatsapp));

        // Combined demo stats
        NeoAnim.countUp(findViewById(R.id.statTotal), 0, 637, 900);
        NeoAnim.countUp(findViewById(R.id.statSuccess), 0, 598, 1000);
        NeoAnim.countUp(findViewById(R.id.statFailed), 0, 38, 800);
        NeoAnim.countUp(findViewById(R.id.statRemaining), 0, 1, 600);

        View btnApply = findViewById(R.id.btnApply);
        NeoAnim.attachPress(btnApply);
        btnApply.setOnClickListener(v ->
                Toast.makeText(this, "Channels updated",
                        Toast.LENGTH_SHORT).show());

        NeoAnim.enterScreen(findViewById(android.R.id.content));
    }

    @Override
    public void onBackPressed() { Nav.back(this); }
}
