<template>
  <el-form :model="form" label-width="120px">
    <el-form-item label="任务名称" required>
      <el-input v-model="form.name" placeholder="输入任务名称" />
    </el-form-item>

    <el-form-item label="描述">
      <el-input v-model="form.description" type="textarea" :rows="3" />
    </el-form-item>

    <el-form-item label="目标URL">
      <el-input v-model="form.target_url" placeholder="https://example.com" />
    </el-form-item>

    <el-form-item label="最大采集数量">
      <el-input-number v-model="form.max_items" :min="1" :max="10000" placeholder="不限" controls-position="right" style="width: 200px" />
    </el-form-item>

    <el-form-item label="Prompt模板">
      <el-select v-model="form.prompt_id" placeholder="选择Prompt">
        <el-option v-for="p in prompts" :key="p.id" :label="p.name" :value="p.id" />
      </el-select>
    </el-form-item>

    <el-form-item label="LLM配置">
      <el-select v-model="form.llm_config_id" placeholder="选择LLM">
        <el-option v-for="c in llmConfigs" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
    </el-form-item>

    <el-form-item label="调度类型" required>
      <el-select v-model="form.schedule.type">
        <el-option label="一次性" value="once" />
        <el-option label="每天" value="daily" />
        <el-option label="每周" value="weekly" />
        <el-option label="自定义" value="custom" />
      </el-select>
    </el-form-item>

    <el-form-item v-if="form.schedule.type === 'daily' || form.schedule.type === 'once'" label="执行时间">
      <el-time-picker v-model="scheduleTime" format="HH:mm" />
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { usePromptsStore } from '@/stores/prompts'
import { useLLMStore } from '@/stores/llm'

const promptsStore = usePromptsStore()
const llmStore = useLLMStore()

const props = defineProps<{
  modelValue: {
    name: string
    description?: string
    target_url?: string
    max_items?: number
    requires_login?: boolean
    prompt_id?: number
    llm_config_id?: number
    schedule: {
      type: string
      time?: string
    }
  }
}>()

const emit = defineEmits<{
  'update:modelValue': [value: any]
}>()

const form = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const scheduleTime = ref<string>()

watch(scheduleTime, (val) => {
  if (val) {
    const date = new Date(val)
    form.value.schedule.time = `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  }
})

const prompts = computed(() => promptsStore.prompts)
const llmConfigs = computed(() => llmStore.configs)
</script>
