# pip install pyautogui

# 配置
pyautogui.FAILSAFE = True # 安全机制: 将鼠标快速移动到屏幕左上角触发异常停止程序 

# 鼠标控制 
pyautogui.position() # 当前鼠标x,y坐标 
pyautogui.size() # 获取屏幕的宽度和高度 
pyautogui.onScreen(x, y) # 检测坐标是否在屏幕内
pyautogui.moveTo(x, y, duration=1) # 将鼠标移动到目标坐标, duration 控制移动耗时 (s)
pyautogui.moveRel(xOffset, yOffset) # 将鼠标相对当前位置进行移动
pyautogui.click(x, y, button='left') # button="left / middle / right"
pyautogui.doubleClick(x, y) 
pyautogui.scroll(amount, x, y) # amount参数正数则向上滚动,负数则向下滚动
pyautogui.dragTo(x, y, duration=1) # 按照鼠标左键拖拽到(x, y)
pyautogui.dragRel(xOffset, yOffset) # 按照鼠标左键相对当前位置拖拽 

# 键盘控制 
print(pyautogui.KEYBOARD_KEYS) # 查看所有可用的按键名称 
pyautogui.write("str", interval=0.25) # 输入字符串 设置每个字符插入间隔0.25秒 
pyautogui.press("enter") # 按下并释放一个按键 
pyautogui.keyDown("ctrl") # 按下按键不释放 
pyautogui.keyUp("ctrl") # 释放按键
pyautogui.hotkey("ctrl", "c") # 按下组合键并释放 

# 屏幕截图 
pillow_image = pyautogui.screenshot() # 屏幕截图然后返回一个Pillow的Image对象 
pyautogui.screenshot('xxx.png') # 截取全屏并且保存为文件 
pillow_image = pyautogui.screenshot(region=(x, y, w, h)) # 截取区域屏幕 左上 宽高 

# 图像识别
location = pyautogui.locationOnScreen('xxx.png') # 查找屏幕上对应的图像并且返回一个 (左, 上, 宽, 高) 位置元组
center_position = pyautogui.locateCenterOnScreen("xxx.png") # 查找屏幕上对应的图像返回 中心点 (x, y) 坐标
pyautogui.click("xxx.png") # 查找图像并且点击中心位置 
# 注意: 从 0.9.41 版本开始，如果 locateOnScreen() 找不到图像，会抛出 ImageNotFoundException 异常，而不是返回 None

# 消息框
pyautogui.alert('临时暂停') 
choice = pyautogui.confirm('请选择选项:', buttons=['A', 'B', 'C'])
