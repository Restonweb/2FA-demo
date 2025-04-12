# Two-Factor Authentication (2FA) Demo / 双因素认证演示



## Introduction / 简介

A Flask-based web application demonstrating Time-based One-Time Password (TOTP) two-factor authentication.  
一个基于Flask的演示时间型一次性密码(TOTP)双因素认证的Web应用。

## TOTP Principle / TOTP原理
 
TOTP (Time-based One-Time Password) is an algorithm that generates temporary passcodes using the current time as a source of uniqueness. It works by:
1. Server and client share a secret key
2. Both sides generate a code based on current timestamp and the secret
3. The code refreshes every 30 seconds
4. User enters the current code to verify identity
 
TOTP(基于时间的一次性密码)是一种使用当前时间作为唯一性源的算法，工作原理：
1. 服务端和客户端共享一个密钥
2. 双方基于当前时间戳和密钥生成代码
3. 代码每30秒刷新一次
4. 用户输入当前代码验证身份

## Features / 功能特点

- User registration and login / 用户注册和登录
- 2FA setup with QR code / 二维码设置2FA
- Real-time code generation / 实时验证码生成
- Countdown timer visualization / 倒计时可视化
- Secure session management / 安全的会话管理

## Installation / 安装

```bash
# Clone repository / 克隆仓库
git clone [[repository-url]](https://github.com/Restonweb/2FA-demo.git)
cd 2FA

# Install dependencies / 安装依赖
pip install -r requirements.txt

# Initialize database / 初始化数据库
flask init-db

# Run application / 运行应用
python app.py
```

## Usage / 使用说明

1. Register a new account  
   注册新账户
2. Login and setup 2FA  
   登录并设置2FA
3. Scan QR code with authenticator app (Google Authenticator, Authy etc.)  
   使用验证器应用(如Google Authenticator)扫描二维码
4. Enter verification code  
   输入验证码
5. After setup, login requires both password and 2FA code  
   设置后，登录需要密码和2FA验证码

## Project Structure / 项目结构

```
2FA/
├── app.py                # Main application
├── requirements.txt      # Dependencies
├── static/
│   └── styles.css        # CSS styles
├── templates/            # HTML templates
└── models.py             # Database models
