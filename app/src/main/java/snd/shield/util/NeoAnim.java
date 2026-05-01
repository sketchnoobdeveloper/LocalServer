package snd.shield.util;

import android.animation.ObjectAnimator;
import android.animation.AnimatorSet;
import android.animation.ValueAnimator;
import android.view.MotionEvent;
import android.view.View;
import android.view.animation.OvershootInterpolator;
import android.view.animation.DecelerateInterpolator;
import android.view.animation.Animation;
import android.view.animation.AnimationUtils;

import androidx.annotation.NonNull;

import snd.shield.R;

/**
 * Smooth click / press / reveal animation helpers used across the app.
 * Apply {@link #attachPress(View)} to any tappable view to get the
 * neomorphism press-bounce feel + accessibility-friendly click handling.
 */
public final class NeoAnim {

    private NeoAnim() {}

    public static void attachPress(@NonNull final View view) {
        view.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                switch (event.getActionMasked()) {
                    case MotionEvent.ACTION_DOWN:
                        animateScale(v, 0.96f, 120, new DecelerateInterpolator());
                        break;
                    case MotionEvent.ACTION_UP:
                    case MotionEvent.ACTION_CANCEL:
                        animateScale(v, 1.0f, 220, new OvershootInterpolator(2.4f));
                        break;
                }
                return false;
            }
        });
    }

    public static void attachPressAll(@NonNull View root, int... ids) {
        for (int id : ids) {
            View v = root.findViewById(id);
            if (v != null) attachPress(v);
        }
    }

    public static void animateScale(@NonNull View v, float scale,
                                    long duration,
                                    android.view.animation.Interpolator interp) {
        ObjectAnimator sx = ObjectAnimator.ofFloat(v, "scaleX", scale);
        ObjectAnimator sy = ObjectAnimator.ofFloat(v, "scaleY", scale);
        AnimatorSet set = new AnimatorSet();
        set.playTogether(sx, sy);
        set.setDuration(duration);
        set.setInterpolator(interp);
        set.start();
    }

    public static void enterScreen(@NonNull View root) {
        Animation a = AnimationUtils.loadAnimation(root.getContext(), R.anim.slide_up);
        root.startAnimation(a);
    }

    public static void fadeIn(@NonNull View v) {
        v.setAlpha(0f);
        v.animate().alpha(1f).setDuration(280).setInterpolator(new DecelerateInterpolator()).start();
    }

    public static void countUp(@NonNull final android.widget.TextView tv,
                               final int from, final int to, long duration) {
        ValueAnimator va = ValueAnimator.ofInt(from, to);
        va.setDuration(duration);
        va.setInterpolator(new DecelerateInterpolator());
        va.addUpdateListener(animation ->
                tv.setText(String.valueOf(animation.getAnimatedValue())));
        va.start();
    }

    public static void pulse(@NonNull View v) {
        Animation a = AnimationUtils.loadAnimation(v.getContext(), R.anim.pulse);
        v.startAnimation(a);
    }
}
