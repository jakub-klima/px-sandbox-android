package com.pxsandbox.appexplorer

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class AppListAdapter(
    private val items: List<AppEntry>,
    private val onClick: (AppEntry) -> Unit,
) : RecyclerView.Adapter<AppListAdapter.AppViewHolder>() {

    class AppViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val icon: ImageView = view.findViewById(R.id.appIcon)
        val label: TextView = view.findViewById(R.id.appLabel)
        val pkg: TextView = view.findViewById(R.id.appPackage)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): AppViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_app, parent, false)
        return AppViewHolder(view)
    }

    override fun onBindViewHolder(holder: AppViewHolder, position: Int) {
        val entry = items[position]
        holder.icon.setImageDrawable(entry.icon)
        holder.label.text = entry.label
        holder.pkg.text = entry.packageName
        holder.itemView.setOnClickListener { onClick(entry) }
    }

    override fun getItemCount(): Int = items.size
}
