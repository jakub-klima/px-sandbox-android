pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "px-sandbox-android"

// Auto-include every app living under apps/<name> that has a build.gradle.kts.
// Adding a new app is just a matter of dropping a new folder in apps/.
val appsDir = file("apps")
if (appsDir.isDirectory) {
    appsDir.listFiles()?.sortedBy { it.name }?.forEach { dir ->
        if (dir.isDirectory && file("${dir.path}/build.gradle.kts").exists()) {
            val moduleName = ":apps:${dir.name}"
            include(moduleName)
            project(moduleName).projectDir = dir
        }
    }
}
