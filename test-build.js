const fs = require('fs');
const path = require('path');

// 检查构建输出目录结构
function checkBuildOutput() {
  const distPath = path.join(__dirname, 'frontend', 'dist');
  
  console.log('检查构建输出目录:', distPath);
  
  if (!fs.existsSync(distPath)) {
    console.error('❌ dist目录不存在');
    return false;
  }
  
  // 检查必需文件
  const requiredFiles = [
    'index.html',
    'static/js',
    'static/css'
  ];
  
  let allExists = true;
  
  requiredFiles.forEach(file => {
    const filePath = path.join(distPath, file);
    if (fs.existsSync(filePath)) {
      console.log('✅', file, '存在');
    } else {
      console.log('❌', file, '不存在');
      allExists = false;
    }
  });
  
  // 列出所有文件
  console.log('\n构建输出文件列表:');
  function listFiles(dir, prefix = '') {
    const files = fs.readdirSync(dir);
    files.forEach(file => {
      const filePath = path.join(dir, file);
      const stat = fs.statSync(filePath);
      if (stat.isDirectory()) {
        console.log(prefix + '📁', file + '/');
        listFiles(filePath, prefix + '  ');
      } else {
        console.log(prefix + '📄', file);
      }
    });
  }
  
  listFiles(distPath);
  
  return allExists;
}

if (require.main === module) {
  checkBuildOutput();
}

module.exports = { checkBuildOutput };