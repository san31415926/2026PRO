<template>
  <div class="seckill-settings">
    <el-card>
        <template #header><span>⚙️ 秒杀规则设置</span></template>
        <el-form label-width="150px" style="max-width: 600px; margin-top: 20px;">
            <el-form-item label="秒杀限时时长"><el-input-number v-model="systemConfig.seckill_time_limit" :min="1" :max="60" /><span style="color:gray; margin-left:10px;">分钟 (用户下单后需在此时间内支付)</span></el-form-item>
            <el-form-item><el-button type="primary" @click="saveSystemConfig">保存秒杀设置</el-button></el-form-item>
        </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const systemConfig = reactive({ group_buy_people: 2, seckill_time_limit: 5, group_buy_discount: 0.8 })

const loadConfig = async () => {
    try {
        const res = await axios.get('http://localhost:5000/api/common/config');
        if(res.data.code === 200) {
            systemConfig.group_buy_people = parseInt(res.data.data.group_buy_people);
            systemConfig.seckill_time_limit = parseInt(res.data.data.seckill_time_limit);
            systemConfig.group_buy_discount = parseFloat(res.data.data.group_buy_discount)
        }
    } catch(e) { ElMessage.error('加载配置失败') }
}

const saveSystemConfig = async () => {
    try {
        await axios.post('http://localhost:5000/api/admin/config', systemConfig);
        ElMessage.success('设置已保存');
    } catch(e) { ElMessage.error('保存失败') }
}

onMounted(() => {
    loadConfig()
})
</script>
