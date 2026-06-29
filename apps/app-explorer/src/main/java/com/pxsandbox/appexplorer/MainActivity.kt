package com.pxsandbox.appexplorer

import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.drawable.Drawable
import android.os.Bundle
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView

/** An installed app: its label, package name and launcher icon. */
data class AppEntry(
    val label: String,
    val packageName: String,
    val icon: Drawable,
)

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val apps = loadInstalledApps()

        findViewById<TextView>(R.id.subtitle).text =
            getString(R.string.app_count, apps.size)

        findViewById<RecyclerView>(R.id.recycler).apply {
            layoutManager = LinearLayoutManager(this@MainActivity)
            adapter = AppListAdapter(apps) { entry -> launchApp(entry) }
        }
    }

    /**
     * Query the system for every app exposing a launcher activity. This kind
     * of access to the device's app inventory is simply not available to a
     * web page running in a browser.
     */
    private fun loadInstalledApps(): List<AppEntry> {
        val pm = packageManager
        val launcherIntent = Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER)
        val resolved = pm.queryIntentActivities(launcherIntent, 0)

        return resolved
            .map { info ->
                AppEntry(
                    label = info.loadLabel(pm).toString(),
                    packageName = info.activityInfo.packageName,
                    icon = info.loadIcon(pm),
                )
            }
            .distinctBy { it.packageName }
            .sortedBy { it.label.lowercase() }
    }

    private fun launchApp(entry: AppEntry) {
        val intent = packageManager.getLaunchIntentForPackage(entry.packageName)
        if (intent != null) {
            startActivity(intent)
        } else {
            Toast.makeText(this, R.string.cannot_launch, Toast.LENGTH_SHORT).show()
        }
    }
}
