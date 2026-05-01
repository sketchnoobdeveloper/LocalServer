package snd.shield;

import android.os.Bundle;
import android.view.View;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import snd.shield.util.Nav;
import snd.shield.util.NeoAnim;

public class EmailFilterActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_email_filter);

        View header = findViewById(R.id.header);
        ((TextView) header.findViewById(R.id.headerTitle))
                .setText(R.string.tool_email_filter);
        View back = header.findViewById(R.id.btnBack);
        NeoAnim.attachPress(back);
        back.setOnClickListener(v -> Nav.back(this));
        NeoAnim.attachPress(header.findViewById(R.id.btnAction));

        View btnApply = findViewById(R.id.btnApply);
        View btnClear = findViewById(R.id.btnClear);
        NeoAnim.attachPress(btnApply);
        NeoAnim.attachPress(btnClear);

        btnApply.setOnClickListener(v -> {
            EditText emailV = findViewById(R.id.inputEmail);
            if (emailV.getText().toString().trim().isEmpty()) {
                emailV.setError("Required");
                return;
            }
            NeoAnim.countUp(findViewById(R.id.statTotal), 0, 412, 800);
            NeoAnim.countUp(findViewById(R.id.statSuccess), 0, 388, 900);
            NeoAnim.countUp(findViewById(R.id.statFailed), 0, 24, 700);
            NeoAnim.countUp(findViewById(R.id.statRemaining), 0, 0, 600);
            Toast.makeText(this, "Filter rule saved", Toast.LENGTH_SHORT).show();
        });

        btnClear.setOnClickListener(v -> {
            ((EditText) findViewById(R.id.inputEmail)).setText("");
            ((EditText) findViewById(R.id.inputSubject)).setText("");
            ((EditText) findViewById(R.id.inputKeywords)).setText("");
        });

        NeoAnim.enterScreen(findViewById(android.R.id.content));
    }

    @Override
    public void onBackPressed() { Nav.back(this); }
}
