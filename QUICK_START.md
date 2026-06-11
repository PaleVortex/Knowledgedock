# QUICK START - Knowledgedock Application

## 🎉 Your Application is Ready!

Your standalone **Knowledgedock** application has been successfully built and is ready to use!

---

## ⚡ Launch in 3 Ways

### Method 1: Double-Click (Easiest) ⭐
```
dist/Knowledgedock.exe
```
Simply click the executable to launch the application.

### Method 2: Use Launch Script
**Windows Batch:**
```batch
launch.bat
```

**PowerShell:**
```powershell
.\launch.ps1
```

### Method 3: Run from Command Line
```bash
cd dist
Knowledgedock.exe
```

### Running with backend (development)
You can start a local HTTP backend and have the GUI talk to it. This is useful
for separating data/storage logic or running multiple clients.

```bash
# start backend only
python backend.py

# start GUI + backend together
python main.py --run-backend

# start GUI using remote manager (assumes backend already running)
python main.py --remote
```

After launching with `--remote`, all bookmark operations go through
`http://127.0.0.1:5000` rather than the local SQLite database.

---

## 📊 Application Statistics

| Item | Details |
|------|---------|
| **Executable Size** | ~118 MB |
| **Location** | `dist/Knowledgedock.exe` |
| **Type** | Standalone (No Python needed) |
| **Platform** | Windows 7+ |
| **Requirements** | 4 GB RAM, 200 MB disk space |

---

## ✨ Features

- 📚 **Multi-Source Learning Aggregator** - Wikipedia, arXiv, OpenLibrary, DOAJ, Crossref
- 🔌 **Plugin Architecture** - Easily extend with custom integrations
- 💾 **Local Database** - SQLite-based storage and caching
- 📑 **Bookmark Management** - Organize and save your resources
- 📥 **Download Manager** - Batch download learning materials
- 🔍 **Full-Text Search** - Find resources quickly
- 💻 **Modern Desktop UI** - Intuitive PyQt5 interface
- 📖 **Built-in Reader** - Read PDFs and documents offline
- 🏷️ **Project Management** - Organize resources by projects and tags
- 📝 **Annotation Support** - Take notes and highlight content

---

## 🎯 First Run Checklist

- [ ] Launch the application using one of the methods above
- [ ] Set up your preferences (File → Settings)
- [ ] Explore available integrations (Extensions tab)
- [ ] Search for your first learning resource
- [ ] Download a resource to try offline reading
- [ ] Create a project to organize your materials

---

## 📖 User Guide

### Searching Resources
1. Use the search bar on the Home tab
2. Select which sources to search (Wikipedia, arXiv, etc.)
3. Click Search
4. Browse results and click to preview

### Downloading Resources
1. Click the Downloads tab
2. Search and select resources
3. Click Download
4. Access downloaded files in the Downloads view

### Managing Bookmarks
1. Click the Bookmarks tab
2. Add resources from search results
3. Organize with tags and folders
4. Search your bookmarks

### Creating Projects
1. Click Projects tab
2. Create a new project
3. Add resources to organize by topic
4. Collaborate and share (when enabled)

---

## 🔧 Troubleshooting

### Application Won't Start
- Ensure you're on Windows 7 or later
- Check available disk space
- Try running as administrator
- Look for error logs in `logs/` folder

### Slow Performance
- Close other applications to free RAM
- Clear cache: Settings → Storage → Clear Cache
- Check internet connection for source searches

### Can't Download Resources
- Verify internet connection
- Check if source website is accessible
- Try downloading from different sources

---

## 📦 Sharing Your Application

### Share the Executable
Simply send `dist/Knowledgedock.exe` to others. They can:
- Run it immediately without installation
- No Python or dependencies needed
- Works on any Windows 7+ machine

### Create Installer (Optional)
Want a professional installer? See `INSTALLATION_GUIDE.md` for NSIS instructions.

### Create Portable Package
Distribute as ZIP:
```bash
Compress-Archive -Path "dist/Knowledgedock.exe" -DestinationPath "Knowledgedock-Portable.zip"
```

---

## 🔄 Updating the Application

To update the application with new features:

1. **Modify source code** in `muhon_app/` directory
2. **Test changes**: `python main.py`
3. **Rebuild executable**: `python build_app.py`
4. **Find updated executable** in `dist/` folder
5. **Distribute** the new `Knowledgedock.exe`

---

## 📚 Additional Resources

- **Technical Details**: Read `README.md`
- **Installation Guide**: See `INSTALLATION_GUIDE.md`
- **Architecture Overview**: Check `README.md` for system design
- **Development**: See `requirements-dev.txt` for dev tools

---

## 🎓 Project Architecture Highlights

Knowledgedock demonstrates advanced software engineering concepts:

✅ **Plugin Architecture** - Open-Closed Principle with extension system
✅ **Data Normalization** - Convert disparate API responses to unified model
✅ **Asynchronous UI** - PyQt5 threading for responsive interface
✅ **Database Persistence** - SQLite for local storage and caching
✅ **Clean Architecture** - Separation of concerns across modules

---

## 💡 Tips & Tricks

- **Keyboard Shortcuts**: Use `Ctrl+F` to search quickly
- **Batch Download**: Download multiple resources at once from the Downloads tab
- **Tags**: Use tags to organize resources by topic
- **Annotations**: Highlight and annotate PDFs directly in the reader
- **Projects**: Group related resources in projects for research papers
- **Export**: Export your bookmarks and projects to CSV/JSON

---

## 🚀 Next Steps

### For Users
- Open `Knowledgedock.exe` and start exploring!
- Customize settings to your preference
- Build your personal knowledge base

### For Developers
- Modify and extend the application
- Add new resource integrations
- Create custom plugins
- Rebuild with `python build_app.py`

### For Distribution
- Share the executable with colleagues/friends
- Create GitHub releases
- Set up automatic builds
- Distribute through your platform

---

## 📞 Support

Issues? Questions?

1. Check the logs in `logs/` folder
2. Review `README.md` for architecture details
3. Check individual source websites if search fails
4. Verify internet connection for remote searches

---

**Enjoy using Knowledgedock! Happy learning! 📚✨**

*Last Updated: February 28, 2026*
*Knowledgedock v1.0.0*
