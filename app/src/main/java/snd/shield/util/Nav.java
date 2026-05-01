package snd.shield.util;

import android.app.Activity;
import android.content.Intent;

import androidx.annotation.NonNull;

import snd.shield.R;

public final class Nav {

    private Nav() {}

    public static void to(@NonNull Activity from, @NonNull Class<?> target) {
        from.startActivity(new Intent(from, target));
        from.overridePendingTransition(R.anim.slide_in_right, R.anim.fade_out);
    }

    public static void replace(@NonNull Activity from, @NonNull Class<?> target) {
        to(from, target);
        from.finish();
    }

    public static void back(@NonNull Activity activity) {
        activity.finish();
        activity.overridePendingTransition(R.anim.fade_in, R.anim.slide_out_right);
    }
}
