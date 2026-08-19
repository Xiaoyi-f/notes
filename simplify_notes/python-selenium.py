from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

# => 完整配置：无头、反爬、代理、窗口大小
options = webdriver.ChromeOptions()

# 隐藏自动化检测
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# 服务器部署无头模式（新版headless）
options.add_argument("--headless=new")

# 固定窗口尺寸，防止元素偏移
options.add_argument("--window-size=1920,1080")

# 代理IP（爬虫/Agent常用）
# options.add_argument("--proxy-server=http://127.0.0.1:7890")

# 禁用图片加载，提速
options.add_argument("--blink-settings=imagesEnabled=false")

# 启动浏览器（Chrome/Edge二选一）
browser = webdriver.Chrome(options=options)
# browser = webdriver.Edge(options=options)

# 关键：绕过navigator.webdriver检测
browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
    """
})

# 隐式等待（全局，最多等待10秒查找元素）
browser.implicitly_wait(10)

# => 页面访问 + 显式等待（面试重中之重，禁止time.sleep）
browser.get("https://www.baidu.com")
# 显式等待：等待输入框可点击，超时10s（比sleep稳定）
wait = WebDriverWait(browser, 10, poll_frequency=0.2)
search_input = wait.until(EC.element_to_be_clickable((By.ID, "kw")))

# 多种定位方式（面试必考，不止xpath）
el_id = browser.find_element(By.ID, "kw")
el_name = browser.find_element(By.NAME, "wd")
el_css = browser.find_element(By.CSS_SELECTOR, "input#su")  # CSS选择器
el_xpath = browser.find_element(By.XPATH, '//input[@value="百度一下"]')
el_text = browser.find_element(By.LINK_TEXT, "新闻")
el_part_text = browser.find_element(By.PARTIAL_LINK_TEXT, "百")

# 输入、清空、快捷键
search_input.clear()
search_input.send_keys("AI Agent")
search_input.send_keys(Keys.ENTER)  # 回车搜索

# => 元素信息提取
btn = browser.find_element(By.ID, "su")
text_content = btn.text
tag = btn.tag_name
attr_href = btn.get_attribute("value")
css_color = btn.value_of_css_property("background-color")
is_show = btn.is_displayed()
is_click = btn.is_enabled()

# => 页面滚动 JS执行
# 滚动到元素可见
browser.execute_script("arguments[0].scrollIntoView(true);", btn)
# 滚动到页面底部
browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")

# => 鼠标操作：悬浮、右键、拖拽
actions = ActionChains(browser)

# 悬浮元素
actions.move_to_element(btn).pause(0.5).perform()

# => Alert弹窗处理
# browser.switch_to.alert.accept()  # 确认弹窗
# browser.switch_to.alert.dismiss() # 取消弹窗
# alert_text = browser.switch_to.alert.text

# => iframe 嵌套页面（高频踩坑考点）
# 切入iframe
# browser.switch_to.frame("iframe-id")
# 切回主页面
# browser.switch_to.default_content()

# => Cookie持久化，免重复登录（Agent爬虫必备）
# 保存cookie
# cookies = browser.get_cookies()
# 加载cookie
# for c in cookies:
#     browser.add_cookie(c)
# browser.refresh()

# => 多标签页切换
# 新开标签
browser.execute_script('window.open("https://www.sogou.com")')
all_handles = browser.window_handles
# 切换第二个标签
browser.switch_to.window(all_handles[1])
# 切回首页
browser.switch_to.window(all_handles[0])

# => 下拉框Select
# select_tag = browser.find_element(By.ID, "city")
# select = Select(select_tag)
# select.select_by_index(0)
# select.select_by_value("sh")
# select.select_by_visible_text("上海")

# => 配合BeautifulSoup解析渲染后页面（串联你之前知识点）
html = browser.page_source
soup = BeautifulSoup(html, "html.parser")
links = soup.find_all("a")

# 截图、关闭
browser.save_screenshot("page.png")
# 关闭当前标签
browser.close()
# 彻底关闭浏览器进程
browser.quit()

