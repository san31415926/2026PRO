import { createApp } from 'vue'
import App from './App.vue'

// 1. 引入 Vant (手机端 UI 库)
import Vant from 'vant'
// 2. 引入 Vant 的样式文件 (必须加，不然没颜色)
import 'vant/lib/index.css'

import axios from 'axios'
// 3. 允许跨域携带 Cookie (关键！)
axios.defaults.withCredentials = true

const app = createApp(App)

// 4. 安装插件
app.use(Vant)
app.mount('#app')