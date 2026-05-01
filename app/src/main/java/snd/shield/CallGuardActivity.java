package snd.shield;

import android.os.Bundle;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import snd.shield.util.Nav;
import snd.shield.util.NeoAnim;

public class CallGuardActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_call_guard);

        View header = findViewById(R.id.header);
        ((TextView) header.findViewById(R.id.headerTitle))
                .setText(R.string.tool_call_guard);
        View back = header.findViewById(R.id.btnBack);
        NeoAnim.attachPress(back);
        back.setOnClickListener(v -> Nav.back(this));
        View action = header.findViewById(R.id.btnAction);
        NeoAnim.attachPress(action);

        View btnStart = findViewById(R.id.btnStart);
        View btnStop = findViewById(R.id.btnStop);
        NeoAnim.attachPress(btnStart);
        NeoAnim.attachPress(btnStop);
        btnStart.setOnClickListener(v -> {
            NeoAnim.countUp(findViewById(R.id.statTotal), 0, 87, 800);
            NeoAnim.countUp(findViewById(R.id.statSuccess), 0, 80, 900);
            NeoAnim.countUp(findViewById(R.id.statFailed), 0, 7, 700);
            NeoAnim.countUp(findViewById(R.id.statRemaining), 0, 0, 600);
            Toast.makeText(this, "Call guard active", Toast.LENGTH_SHORT).show();
        });
        btnStop.setOnClickListener(v ->
                Toast.makeText(this, "Call guard paused", Toast.LENGTH_SHORT).show());

        NeoAnim.enterScreen(findViewById(android.R.id.content));
    }

    @Override
    public void onBackPressed() { Nav.back(this); }
}
