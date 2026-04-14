<template>
  <div class="member-page">
    <el-card class="member-card">
      <template #header>
        <div class="member-head">
          <div>
            <div class="member-title">会员列表</div>
            <div class="member-subtitle">高权限会员管理，可修改等级、状态、积分与余额</div>
          </div>
          <el-button @click="loadMembers">刷新列表</el-button>
        </div>
      </template>

      <el-table :data="memberList" border stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="头像" width="84">
          <template #default="{ row }">
            <el-avatar :size="42" :src="row.avatar" />
          </template>
        </el-table-column>
        <el-table-column prop="username" label="账号" min-width="120" />
        <el-table-column prop="nickname" label="昵称" min-width="130" />
        <el-table-column label="会员状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '正常' : '冻结' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="等级" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.level === 1" type="info">普通会员</el-tag>
            <el-tag v-else-if="row.level === 2" class="tag-gold">黄金VIP</el-tag>
            <el-tag v-else type="primary">钻石VIP</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="余额" width="130">
          <template #default="{ row }">
            <span class="amount-text">¥{{ Number(row.balance).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="points" label="积分" width="100" />
        <el-table-column prop="hero_text" label="主页文案" min-width="180" show-overflow-tooltip />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <div class="action-row">
              <el-button size="small" type="primary" plain @click="openManageDialog(row)">管理会员</el-button>
              <el-button size="small" type="danger" plain @click="openRechargeDialog(row)">充值余额</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="rechargeVisible" title="管理员充值" width="380px">
      <div class="dialog-copy">
        <p>为 <b>{{ selectedMember?.nickname }}</b> 充值余额</p>
        <el-input-number v-model="rechargeAmount" :min="1" :max="99999" style="width:100%;margin-top:10px;" />
      </div>
      <template #footer>
        <el-button @click="rechargeVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRecharge">确认充值</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="manageVisible" title="高权限会员管理" width="520px">
      <el-alert
        title="此处修改会直接影响用户登录、会员权益和资产展示，请谨慎操作。"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 18px;"
      />
      <el-form label-width="96px" class="manage-form">
        <el-form-item label="账号">
          <el-input :model-value="manageForm.username" disabled />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="manageForm.nickname" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="会员状态">
          <el-radio-group v-model="manageForm.status">
            <el-radio-button v-for="item in statusOptions" :key="item.value" :label="item.value">
              {{ item.label }}
            </el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="会员等级">
          <el-radio-group v-model="manageForm.level">
            <el-radio-button v-for="item in levelOptions" :key="item.value" :label="item.value">
              {{ item.label }}
            </el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="账户余额">
          <el-input-number v-model="manageForm.balance" :min="0" :precision="2" :step="100" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="账户积分">
          <el-input-number v-model="manageForm.points" :min="0" :step="100" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="主页文案">
          <el-input
            v-model="manageForm.hero_text"
            type="textarea"
            :rows="3"
            maxlength="20"
            show-word-limit
            placeholder="最多 20 个字"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="manageVisible = false">取消</el-button>
        <el-button type="primary" @click="submitMemberManage">保存修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const memberList = ref([])
const rechargeVisible = ref(false)
const manageVisible = ref(false)
const selectedMember = ref(null)
const rechargeAmount = ref(100)
const manageForm = reactive({
  id: null,
  username: '',
  nickname: '',
  status: 1,
  level: 1,
  balance: 0,
  points: 0,
  hero_text: '',
})

const statusOptions = [
  { label: '正常', value: 1 },
  { label: '冻结', value: 2 },
]

const levelOptions = [
  { label: '普通', value: 1 },
  { label: '黄金VIP', value: 2 },
  { label: '钻石VIP', value: 3 },
]

const loadMembers = async () => {
  const res = await axios.get('http://localhost:5000/api/admin/members')
  if (res.data.code === 200) {
    memberList.value = res.data.data
  } else {
    ElMessage.error(res.data.msg || '加载会员失败')
  }
}

const openRechargeDialog = (row) => {
  selectedMember.value = row
  rechargeAmount.value = 100
  rechargeVisible.value = true
}

const openManageDialog = (row) => {
  selectedMember.value = row
  manageForm.id = row.id
  manageForm.username = row.username
  manageForm.nickname = row.nickname
  manageForm.status = row.status ?? 1
  manageForm.level = row.level ?? 1
  manageForm.balance = Number(row.balance || 0)
  manageForm.points = Number(row.points || 0)
  manageForm.hero_text = row.hero_text || ''
  manageVisible.value = true
}

const submitRecharge = async () => {
  const res = await axios.post('http://localhost:5000/api/admin/member/recharge', {
    user_id: selectedMember.value.id,
    amount: rechargeAmount.value,
  })
  if (res.data.code === 200) {
    ElMessage.success('充值成功')
    rechargeVisible.value = false
    loadMembers()
  } else {
    ElMessage.error(res.data.msg || '操作失败')
  }
}

const submitMemberManage = async () => {
  const payload = {
    nickname: manageForm.nickname,
    status: manageForm.status,
    level: manageForm.level,
    balance: manageForm.balance,
    points: manageForm.points,
    hero_text: manageForm.hero_text,
  }
  const res = await axios.put(`http://localhost:5000/api/admin/member/${manageForm.id}`, payload)
  if (res.data.code === 200) {
    ElMessage.success('会员信息已更新')
    manageVisible.value = false
    loadMembers()
  } else {
    ElMessage.error(res.data.msg || '保存失败')
  }
}

onMounted(loadMembers)
</script>

<style scoped>
.member-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.member-card {
  border-radius: 18px;
}

.member-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.member-title {
  font-size: 24px;
  font-weight: 800;
  color: #2d2f33;
}

.member-subtitle {
  margin-top: 6px;
  font-size: 13px;
  color: #8b93a6;
}

.amount-text {
  color: #f56c6c;
  font-weight: 700;
}

.tag-gold {
  background: #ffd700;
  border-color: #ffd700;
  color: #333;
}

.action-row {
  display: flex;
  gap: 8px;
}

.dialog-copy {
  padding: 10px 0;
}

.manage-form :deep(.el-input-number) {
  width: 100%;
}
</style>
