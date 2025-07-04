<template>
  <h1>成绩水平测算</h1>
  <p>请输入你的分数：</p>
  <input v-model.number="score" type="number" />

  <p>请输入满分：</p>
  <input v-model.number="fullScore" type="number" />

  <button @click="calc">计算</button>

  <div v-if="result">
    <p>你的分数占比：{{ result }}%</p>
    <p>评价：{{ level }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const score = ref(0)
const fullScore = ref(100)
const result = ref('')
const level = ref('')

function calc() {
  if (fullScore.value === 0) {
    result.value = '满分不能为 0'
    level.value = ''
    return
  }
  const percent = ((score.value / fullScore.value) * 100).toFixed(2)
  result.value = percent

  if (percent >= 90) {
    level.value = '优秀'
  } else if (percent >= 75) {
    level.value = '良好'
  } else if (percent >= 60) {
    level.value = '及格'
  } else {
    level.value = '不及格'
  }
}
</script>

<style scoped>
h1 {
  color: #42b983;
}
</style>
