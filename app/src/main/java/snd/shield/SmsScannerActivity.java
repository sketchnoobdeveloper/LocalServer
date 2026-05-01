package snd.shield;

import android.os.Bundle;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import snd.shield.util.Nav;
import snd.shield.util.NeoAnim;

public class SmsScannerActivity extends AppCompatActivity {

    private boolean running = false;
    private int total, success, failed, remaining;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_sms_scanner);

        // Header
        View header = findViewById(R.id.header);
        TextView title = header.findViewById(R.id.headerTitle);
        title.setText(R.string.tool_sms_scanner);
        View back = header.findViewById(R.id.btnBack);
        View action = header.findViewById(R.id.btnAction);
        NeoAnim.attachPress(back);
        NeoAnim.attachPress(action);
        back.setOnClickListener(v -> Nav.back(this));
        action.setOnClickListener(v ->
                Toast.makeText(this, "Open scan history",
                        Toast.LENGTH_SHORT).show());

        // Buttons
        View btnStart = findViewById(R.id.btnStart);
        View btnStop = findViewById(R.id.btnStop);
        NeoAnim.attachPress(btnStart);
        NeoAnim.attachPress(btnStop);

        btnStart.setOnClickListener(v -> {
            if (running) return;
            running = true;
            seedDemoStats();
            Toast.makeText(this, "Scanner started",
                    Toast.LENGTH_SHORT).show();
        });
        btnStop.setOnClickListener(v -> {
            running = false;
            Toast.makeText(this, "Scanner stopped",
                    Toast.LENGTH_SHORT).show();
        });

        NeoAnim.enterScreen(findViewById(android.R.id.content));
    }

    private void seedDemoStats() {
        total = 124; success = 118; failed = 6; remaining = 0;
        NeoAnim.countUp(findViewById(R.id.statTotal), 0, total, 800);
        NeoAnim.countUp(findViewById(R.id.statSuccess), 0, success, 900);
        NeoAnim.countUp(findViewById(R.id.statFailed), 0, failed, 700);
        NeoAnim.countUp(findViewById(R.id.statRemaining), 0, remaining, 600);
    }

    @Override
    public void onBackPressed() { Nav.back(this); }
}
