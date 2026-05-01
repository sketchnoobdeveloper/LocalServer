package snd.shield;

import android.animation.ObjectAnimator;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.view.animation.OvershootInterpolator;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import snd.shield.util.NeoAnim;

public class SplashActivity extends AppCompatActivity {

    private static final long SPLASH_DURATION_MS = 1800L;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);

        View logoBg = findViewById(R.id.logoBg);
        ImageView logo = findViewById(R.id.logo);
        TextView appName = findViewById(R.id.appName);
        TextView appTagline = findViewById(R.id.appTagline);

        // Logo entrance: scale + rotate
        logoBg.setScaleX(0.4f); logoBg.setScaleY(0.4f); logoBg.setAlpha(0f);
        logoBg.animate().scaleX(1f).scaleY(1f).alpha(1f)
                .setDuration(620).setInterpolator(new OvershootInterpolator(2.2f)).start();

        ObjectAnimator rotate = ObjectAnimator.ofFloat(logo, "rotationY", 0f, 360f);
        rotate.setDuration(900);
        rotate.setStartDelay(200);
        rotate.start();

        // Name + tagline staggered fade
        appName.setAlpha(0f); appName.setTranslationY(24f);
        appName.animate().alpha(1f).translationY(0f)
                .setStartDelay(380).setDuration(420).start();

        appTagline.setAlpha(0f); appTagline.setTranslationY(20f);
        appTagline.animate().alpha(1f).translationY(0f)
                .setStartDelay(520).setDuration(420).start();

        // Subtle pulse
        NeoAnim.pulse(logoBg);

        new Handler(Looper.getMainLooper()).postDelayed(this::routeNext, SPLASH_DURATION_MS);
    }

    private void routeNext() {
        // TODO: read auth state from prefs / API; route accordingly
        boolean loggedIn = false;
        Intent intent = new Intent(this,
                loggedIn ? ManageToolsActivity.class : LoginActivity.class);
        startActivity(intent);
        overridePendingTransition(R.anim.fade_in, R.anim.fade_out);
        finish();
    }
}
