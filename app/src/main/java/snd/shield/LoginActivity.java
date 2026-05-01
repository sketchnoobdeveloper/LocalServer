package snd.shield;

import android.os.Bundle;
import android.text.InputType;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import snd.shield.util.Nav;
import snd.shield.util.NeoAnim;

public class LoginActivity extends AppCompatActivity {

    private boolean passwordVisible = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        final EditText inputEmail = findViewById(R.id.inputEmail);
        final EditText inputPassword = findViewById(R.id.inputPassword);
        final ImageView btnToggle = findViewById(R.id.btnTogglePassword);
        final View btnLogin = findViewById(R.id.btnLogin);
        final View btnForgot = findViewById(R.id.btnForgot);
        final View btnGoogle = findViewById(R.id.btnGoogle);
        final View btnFacebook = findViewById(R.id.btnFacebook);
        final View btnSignup = findViewById(R.id.btnSignup);

        NeoAnim.attachPress(btnLogin);
        NeoAnim.attachPress(btnGoogle);
        NeoAnim.attachPress(btnFacebook);
        NeoAnim.attachPress(btnToggle);
        NeoAnim.attachPress(btnForgot);
        NeoAnim.attachPress(btnSignup);

        // Staggered entrance for the form
        NeoAnim.enterScreen(findViewById(android.R.id.content));

        btnToggle.setOnClickListener(v -> {
            passwordVisible = !passwordVisible;
            int sel = inputPassword.getSelectionEnd();
            inputPassword.setInputType(passwordVisible
                    ? InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD
                    : InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
            inputPassword.setSelection(Math.max(0, sel));
        });

        btnLogin.setOnClickListener(v -> attemptLogin(inputEmail, inputPassword));
        btnForgot.setOnClickListener(v ->
                toast("Forgot password flow — wire to your auth backend"));
        btnGoogle.setOnClickListener(v -> toast("Google sign-in — TODO"));
        btnFacebook.setOnClickListener(v -> toast("Facebook sign-in — TODO"));
        btnSignup.setOnClickListener(v -> toast("Sign up — TODO"));
    }

    private void attemptLogin(EditText emailV, EditText passV) {
        String email = emailV.getText().toString().trim();
        String pass = passV.getText().toString();
        if (email.isEmpty() || !android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            emailV.setError("Enter a valid email");
            return;
        }
        if (pass.length() < 6) {
            passV.setError("Password too short");
            return;
        }
        // TODO: replace with real auth (Firebase / API)
        toast("Logged in (stub)");
        Nav.replace(this, ManageToolsActivity.class);
    }

    private void toast(String s) {
        Toast.makeText(this, s, Toast.LENGTH_SHORT).show();
    }

    @Override
    public void onBackPressed() {
        super.onBackPressed();
        overridePendingTransition(R.anim.fade_in, R.anim.slide_out_right);
    }
}
