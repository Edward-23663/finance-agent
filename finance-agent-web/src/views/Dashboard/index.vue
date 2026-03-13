<template>
  <div class="dashboard-container">
    <el-card class="analysis-form-card">
      <template #header>
        <div class="card-header">
          <span>发起新的金融分析</span>
        </div>
      </template>
      
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" size="large">
        <el-form-item label="分析标的" prop="ticker">
          <el-input 
            v-model="form.ticker" 
            placeholder="请输入股票代码 (如: 600519)" 
            clearable
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>

        <el-form-item label="分析维度" prop="dimensions">
          <el-checkbox-group v-model="form.dimensions">
            <el-checkbox label="fundamental" border>基本面分析</el-checkbox>
            <el-checkbox label="valuation" border>多模型估值</el-checkbox>
            <el-checkbox label="sentiment" border>舆情分析</el-checkbox>
            <el-checkbox label="catalyst" border>催化剂分析</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm(formRef)" :loading="submitting" class="submit-btn">
            启动智能体分析
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, type FormInstance, type FormRules } from 'element-plus';
import { Search } from '@element-plus/icons-vue';
import { submitAnalysisTask } from '@/api/instance';
import { useAnalysisStore } from '@/stores/analysisStore';

const router = useRouter();
const analysisStore = useAnalysisStore();
const formRef = ref<FormInstance>();
const submitting = ref(false);

const form = reactive({
  ticker: '',
  dimensions: ['fundamental', 'valuation'],
  params: {}
});

const rules = reactive<FormRules>({
  ticker: [{ required: true, message: '请输入股票代码', trigger: 'blur' }],
  dimensions: [{ type: 'array', required: true, message: '请至少选择一个分析维度', trigger: 'change' }],
});

const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return;
  await formEl.validate(async (valid) => {
    if (valid) {
      submitting.value = true;
      try {
        const response = await submitAnalysisTask({
          ticker: form.ticker,
          dimensions: form.dimensions as any,
          params: form.params
        });
        const { trace_id } = response.data;
        
        ElMessage.success(`任务已提交，Trace ID: ${trace_id}`);
        analysisStore.setTraceId(trace_id);
        router.push({ name: 'Report', params: { traceId: trace_id } });

      } catch (error) {
        console.error('Failed to submit task:', error);
        ElMessage.error('任务提交失败，请检查服务状态');
      } finally {
        submitting.value = false;
      }
    }
  });
};
</script>

<style scoped lang="scss">
.dashboard-container {
  display: flex;
  justify-content: center;
  padding-top: 50px;

  .analysis-form-card {
    width: 800px;
    .submit-btn {
        width: 100%;
        font-weight: bold;
    }
  }
}
</style>
