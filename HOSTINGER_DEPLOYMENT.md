# Hostinger Deployment Guide

## Files to Upload

Upload these files to your Hostinger hosting account:

1. **index.html** - Main website file
2. **styles.css** - Stylesheet file  
3. **doctor-photo.jpg** - Optimized doctor photo (38KB)

## Step-by-Step Deployment

### 1. Login to Hostinger
- Go to hpanel.hostinger.com
- Login to your account

### 2. Access File Manager
- Navigate to your hosting plan
- Click on "File Manager" 
- Navigate to the `public_html` folder

### 3. Upload Files
- Delete any existing index.html if present
- Upload the 3 files listed above
- Make sure they are in the root of `public_html`

### 4. Verify Deployment
- Visit your domain (e.g., dranilkumardhar.com)
- Check that the website loads correctly
- Test all buttons and links

## Important Notes

### File Structure
```
public_html/
├── index.html
├── styles.css
└── doctor-photo.jpg
```

### Performance Tips
- Enable GZIP compression in Hostinger settings
- Set up browser caching for better performance
- Consider using Hostinger's CDN if available

### SSL Certificate
- Make sure SSL is enabled for HTTPS
- This is usually free with Hostinger

### Custom Domain
- If you haven't already, point your domain to Hostinger's nameservers
- This is done in your domain registrar's settings

## Troubleshooting

**Website not loading?**
- Check file names are exactly as listed (case-sensitive)
- Ensure index.html is in the root folder
- Clear browser cache

**Images not showing?**
- Verify doctor-photo.jpg is uploaded
- Check the file name matches exactly

**Styles not applying?**
- Ensure styles.css is uploaded
- Check for any console errors in browser

## Future Updates

To update the website:
1. Make changes locally
2. Push to GitHub (for backup)
3. Upload changed files to Hostinger
4. Clear browser cache to see changes

## Contact for Issues
If you face any deployment issues, Hostinger support is available 24/7 through their live chat.