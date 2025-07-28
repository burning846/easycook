import React from 'react';
import { Layout } from 'antd';

const { Footer } = Layout;

function AppFooter() {
  return (
    <Footer style={{ textAlign: 'center' }}>
      EasyCook ©{new Date().getFullYear()} 帮助做饭小程序
    </Footer>
  );
}

export default AppFooter;