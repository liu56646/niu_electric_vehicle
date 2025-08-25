# Niu Electric Vehicle Integration for Home Assistant

这个集成允许你在Home Assistant中监控你的小牛电动车的状态和信息。

## 功能特点
- 监控电池电量
- 查看剩余续航里程
- 监控当前速度
- 追踪总里程
- 监控车辆温度

## 安装方法
1. 通过HACS安装
   - 添加自定义仓库: `https://github.com/liu56646/niu_electric_vehicle.git`
   - 搜索并安装 "Niu Electric Vehicle" 集成

2. 手动安装
   - 下载最新版本的发布包
   - 将文件解压到 `custom_components/niu_electric_vehicle/` 目录
   - 重启Home Assistant

## 配置方法
1. 进入设置 > 设备与服务
2. 点击 + 添加集成
3. 搜索 "Niu Electric Vehicle"
4. 输入你的小牛账号用户名、密码和车辆ID
5. 点击提交

## 可用传感器
- `sensor.niu_battery_level`: 电池电量百分比
- `sensor.niu_range`: 剩余续航里程
- `sensor.niu_current_speed`: 当前速度
- `sensor.niu_total_mileage`: 总里程
- `sensor.niu_temperature`: 车辆温度

## 故障排除
如果遇到问题，请检查以下几点:
1. 确保你的小牛电动车账号信息正确
2. 确保你的车辆已连接到互联网
3. 尝试重启Home Assistant

## 贡献
欢迎提交问题和拉取请求来改进这个组件。

## 免责声明
这个组件与小牛电动车公司没有官方关联，仅作为个人项目开发。