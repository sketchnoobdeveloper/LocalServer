package snd.shield;

import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import snd.shield.util.Nav;
import snd.shield.util.NeoAnim;

public class WhatsappReportActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_whatsapp_report);

        View header = findViewById(R.id.header);
        ((TextView) header.findViewById(R.id.headerTitle))
                .setText(R.string.tool_whatsapp_report);
        View back = header.findViewById(R.id.btnBack);
        NeoAnim.attachPress(back);
        back.setOnClickListener(v -> Nav.back(this));
        NeoAnim.attachPress(header.findViewById(R.id.btnAction));

        Spinner category = findViewById(R.id.inputCategory);
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this,
                android.R.layout.simple_spinner_dropdown_item,
                new String[]{
                        "Spam / Bombing",
                        "Phishing / Scam",
                        "Harassment / Abuse",
                        "Impersonation",
                        "Other"
                });
        category.setAdapter(adapter);

        View btnSubmit = findViewById(R.id.btnSubmit);
        NeoAnim.attachPress(btnSubmit);
        btnSubmit.setOnClickListener(v -> {
            EditText num = findViewById(R.id.inputNumber);
            if (num.getText().toString().trim().isEmpty()) {
                num.setError("Required");
                return;
            }
            NeoAnim.countUp(findViewById(R.id.statTotal), 0, 14, 700);
            NeoAnim.countUp(findViewById(R.id.statSuccess), 0, 12, 800);
            NeoAnim.countUp(findViewById(R.id.statFailed), 0, 1, 600);
            NeoAnim.countUp(findViewById(R.id.statRemaining), 0, 1, 500);
            Toast.makeText(this, "Report submitted", Toast.LENGTH_SHORT).show();
        });

        NeoAnim.enterScreen(findViewById(android.R.id.content));
    }

    @Override
    public void onBackPressed() { Nav.back(this); }
}
