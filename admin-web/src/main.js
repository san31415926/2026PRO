import { createApp } from 'vue'
import App from './App.vue'

// 1. 引入 Element Plus (UI 库)
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 引入中文包 (让日期选择器显示中文)
import zhCn from 'element-plus/es/locale/lang/zh-cn'

// 2. 引入图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// ⚠️⚠️⚠️ 新增下面这两行！让 Axios 携带 Cookie 身份证 ⚠️⚠️⚠️
import axios from 'axios'
axios.defaults.withCredentials = true

const app = createApp(App)

// 3. 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 4. 安装插件
app.use(ElementPlus, { locale: zhCn })
app.mount('#app')