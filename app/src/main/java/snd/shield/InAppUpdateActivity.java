package snd.shield;

import android.animation.ObjectAnimator;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.view.animation.LinearInterpolator;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import snd.shield.util.Nav;
import snd.shield.util.NeoAnim;

public class InAppUpdateActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_in_app_update);

        View header = findViewById(R.id.header);
        ((TextView) header.findViewById(R.id.headerTitle))
                .setText(R.string.tool_in_app_update);
        View back = header.findViewById(R.id.btnBack);
        NeoAnim.attachPress(back);
        back.setOnClickListener(v -> Nav.back(this));
        NeoAnim.attachPress(header.findViewById(R.id.btnAction));

        // Spin the update icon
        View icon = findViewById(R.id.updateIcon);
        ObjectAnimator spin = ObjectAnimator.ofFloat(icon, "rotation", 0f, 360f);
        spin.setRepeatCount(ObjectAnimator.INFINITE);
        spin.setDuration(1400);
        spin.setInterpolator(new LinearInterpolator());
        spin.start();

        final TextView state = findViewById(R.id.updateState);
        final TextView detail = findViewById(R.id.updateDetail);
        final ProgressBar progress = findViewById(R.id.updateProgress);
        final View btnRow = findViewById(R.id.btnRow);
        Button btnUpdate = findViewById(R.id.btnUpdate);
        Button btnLater = findViewById(R.id.btnLater);
        NeoAnim.attachPress(btnUpdate);
        NeoAnim.attachPress(btnLater);

        // Simulated check
        new Handler(Looper.getMainLooper()).postDelayed(() -> {
            spin.cancel();
            icon.setRotation(0f);
            // Pretend an update is available
            state.setText(R.string.update_available);
            detail.setText("Version 1.1 is available with improved spam DB & faster scans.");
            progress.setVisibility(View.GONE);
            btnRow.setVisibility(View.VISIBLE);
            NeoAnim.fadeIn(btnRow);
        }, 1500L);

        btnUpdate.setOnClickListener(v -> startFakeDownload(state, detail, progress, btnRow));
        btnLater.setOnClickListener(v -> Nav.back(this));
    }

    private void startFakeDownload(TextView state, TextView detail,
                                   ProgressBar progress, View btnRow) {
        btnRow.setVisibility(View.GONE);
        progress.setVisibility(View.VISIBLE);
        state.setText("Downloading\u2026");
        detail.setText("Please keep the app open while we update.");

        ObjectAnimator pa = ObjectAnimator.ofInt(progress, "progress", 0, 100);
        pa.setDuration(1800);
        pa.start();

        new Handler(Looper.getMainLooper()).postDelayed(() -> {
            state.setText(R.string.update_uptodate);
            detail.setText("Version 1.1 installed.");
            Toast.makeText(this, "Updated to 1.1", Toast.LENGTH_SHORT).show();
        }, 2000L);
    }

    @Override
    public void onBackPressed() { Nav.back(this); }
}
