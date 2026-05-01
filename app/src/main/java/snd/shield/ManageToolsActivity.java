package snd.shield;

import android.os.Bundle;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.DrawableRes;
import androidx.annotation.IdRes;
import androidx.annotation.StringRes;
import androidx.appcompat.app.AppCompatActivity;

import snd.shield.util.Nav;
import snd.shield.util.NeoAnim;

public class ManageToolsActivity extends AppCompatActivity {

    private boolean protectionOn = true;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_manage_tools);

        // Header settings button
        View btnSettings = findViewById(R.id.btnSettings);
        NeoAnim.attachPress(btnSettings);
        btnSettings.setOnClickListener(v -> Nav.to(this, MyProtectionActivity.class));

        // Hero toggle (master protection switch)
        View heroToggle = findViewById(R.id.heroToggleBg);
        View heroToggleThumb = findViewById(R.id.heroToggleThumb);
        NeoAnim.attachPress(heroToggle);
        heroToggle.setOnClickListener(v -> toggleProtection(heroToggleThumb));

        // Tools
        bindTile(R.id.tileSmsScanner, R.drawable.ic_sms,
                R.string.tool_sms_scanner, R.string.tool_sms_scanner_desc,
                SmsScannerActivity.class);
        bindTile(R.id.tileCallGuard, R.drawable.ic_call,
                R.string.tool_call_guard, R.string.tool_call_guard_desc,
                CallGuardActivity.class);
        bindTile(R.id.tileEmailFilter, R.drawable.ic_email,
                R.string.tool_email_filter, R.string.tool_email_filter_desc,
                EmailFilterActivity.class);
        bindTile(R.id.tileSmsRules, R.drawable.ic_filter,
                R.string.tool_sms_rules, R.string.tool_sms_rules_desc,
                SmsRulesActivity.class);
        bindTile(R.id.tileWhatsapp, R.drawable.ic_whatsapp,
                R.string.tool_whatsapp_report, R.string.tool_whatsapp_report_desc,
                WhatsappReportActivity.class);
        bindTile(R.id.tileMultiGuard, R.drawable.ic_layers,
                R.string.tool_multi_guard, R.string.tool_multi_guard_desc,
                MultiChannelGuardActivity.class);
        bindTile(R.id.tileMyProtection, R.drawable.ic_shield,
                R.string.tool_my_protection, R.string.tool_my_protection_desc,
                MyProtectionActivity.class);
        bindTile(R.id.tileManageUsers, R.drawable.ic_users,
                R.string.tool_manage_users, R.string.tool_manage_users_desc,
                ManageUsersActivity.class);
        bindTile(R.id.tileRequestManager, R.drawable.ic_api,
                R.string.tool_request_manager, R.string.tool_request_manager_desc,
                RequestManagerActivity.class);
        bindTile(R.id.tileSubscription, R.drawable.ic_crown,
                R.string.tool_subscription, R.string.tool_subscription_desc,
                SubscriptionActivity.class);
        bindTile(R.id.tileUpdate, R.drawable.ic_update,
                R.string.tool_in_app_update, R.string.tool_in_app_update_desc,
                InAppUpdateActivity.class);
        bindTile(R.id.tileLogout, R.drawable.ic_lock,
                R.string.action_logout,
                R.string.app_tagline, null);
    }

    private void bindTile(@IdRes int rootId,
                          @DrawableRes int iconRes,
                          @StringRes int titleRes,
                          @StringRes int descRes,
                          final Class<?> target) {
        View root = findViewById(rootId);
        if (root == null) return;
        ImageView icon = root.findViewById(R.id.icon);
        TextView title = root.findViewById(R.id.title);
        TextView subtitle = root.findViewById(R.id.subtitle);
        if (icon != null) icon.setImageResource(iconRes);
        if (title != null) title.setText(titleRes);
        if (subtitle != null) subtitle.setText(descRes);

        NeoAnim.attachPress(root);
        root.setOnClickListener(v -> {
            if (target != null) {
                Nav.to(this, target);
            } else {
                // Logout placeholder
                Toast.makeText(this, "Logout — wire to auth backend",
                        Toast.LENGTH_SHORT).show();
                Nav.replace(this, LoginActivity.class);
            }
        });
    }

    private void toggleProtection(View thumb) {
        protectionOn = !protectionOn;
        TextView heroTitle = findViewById(R.id.heroTitle);
        if (protectionOn) {
            heroTitle.setText(R.string.dashboard_status_protected);
            thumb.animate().translationX(0f).setDuration(220).start();
            thumb.setBackgroundResource(R.drawable.neo_circle_bg);
        } else {
            heroTitle.setText(R.string.dashboard_status_paused);
            float dx = -((float) (thumb.getRootView().getResources()
                    .getDisplayMetrics().density * 24f));
            thumb.animate().translationX(dx).setDuration(220).start();
        }
    }
}
