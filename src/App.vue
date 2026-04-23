<template>
  <div class="dashboard-container">
    <dv-full-screen-container>
      <!-- 顶栏标题 -->
      <div class="header">
        <dv-decoration-8 class="header-decor-left" />
        <div class="header-title">
          <h2>城市交通流量智能时序预测系统</h2>
          <dv-decoration-5 class="header-decor-center" />
        </div>
        <dv-decoration-8 :reverse="true" class="header-decor-right" />
      </div>

      <!-- 主体内容 -->
      <div class="main-content">
        <!-- 左侧数据分析面板 -->
        <div class="side-panel left-panel">
          <dv-border-box-12>
            <div class="panel-inner">
              <h3 class="panel-title">历史交通流量分布 (过去24小时)</h3>
              <div ref="historyChartRef" class="chart-box"></div>
            </div>
          </dv-border-box-12>
        </div>

        <!-- 中央时序预测主面板 (C位) -->
        <div class="center-panel">
          <dv-border-box-11 title="时序预测大图">
            <div class="panel-inner">
              <div v-if="loading" class="loading-wrapper">
                <dv-loading>预测模型计算中...</dv-loading>
              </div>
              <div v-else ref="mainChartRef" class="main-chart-box"></div>
            </div>
          </dv-border-box-11>
        </div>

        <!-- 右侧模型评估面板 -->
        <div class="side-panel right-panel">
          <dv-border-box-12>
            <div class="panel-inner">
              <h3 class="panel-title">模型评估指标与置信度</h3>
              
              <div class="metrics-container">
                <div class="metric-item">
                  <div class="metric-label">均方误差 (RMSE)</div>
                  <div class="metric-value">{{ metrics.rmse }}</div>
                </div>
                <div class="metric-item">
                  <div class="metric-label">平均绝对误差 (MAE)</div>
                  <div class="metric-value">{{ metrics.mae }}</div>
                </div>
              </div>

              <div class="confidence-container">
                <h4 class="confidence-title">预测置信度</h4>
                <dv-active-ring-chart 
                  :config="ringConfig" 
                  style="width:200px;height:200px;margin: 0 auto;" 
                />
              </div>
            </div>
          </dv-border-box-12>
        </div>
      </div>
    </dv-full-screen-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

const historyChartRef = ref<HTMLElement | null>(null)
const mainChartRef = ref<HTMLElement | null>(null)
let historyChartInstance: echarts.ECharts | null = null
let mainChartInstance: echarts.ECharts | null = null

const loading = ref(true)

const metrics = reactive({
  rmse: 0,
  mae: 0,
  confidence: 0
})

const ringConfig = reactive({
  data: [
    { name: '预测置信度', value: 0 }
  ],
  lineWidth: 20,
  color: ['#00baff', '#3de7c9'],
  digitalFlopStyle: {
    fontSize: 24,
    fill: '#fff'
  }
})

// 格式化时间标签
const formatTime = (timeStr: string) => {
  const parts = timeStr.split(' ')
  if(parts.length > 1) {
    const time = parts[1].substring(0, 5) // 取 HH:mm
    return time
  }
  return timeStr
}

// 渲染左侧柱状图
const initHistoryChart = (timestamps: string[], flows: number[]) => {
  if (!historyChartRef.value) return
  
  if (!historyChartInstance) {
    historyChartInstance = echarts.init(historyChartRef.value, 'dark')
  }

  const option = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { top: 30, right: 10, bottom: 30, left: 50 },
    xAxis: {
      type: 'category',
      data: timestamps.map(formatTime),
      axisLabel: { color: '#8892b0', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#8892b0', fontSize: 10 },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
    },
    series: [
      {
        type: 'bar',
        data: flows,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#2378f7' },
              { offset: 0.7, color: '#2378f7' },
              { offset: 1, color: '#83bff6' }
            ])
          }
        }
      }
    ]
  }

  historyChartInstance.setOption(option)
}

// 渲染中央预测主图
const initMainChart = (histTimes: string[], histFlows: number[], predTimes: string[], predFlows: number[]) => {
  if (!mainChartRef.value) return
  
  if (!mainChartInstance) {
    mainChartInstance = echarts.init(mainChartRef.value, 'dark')
  }

  const allTimes = [...histTimes, ...predTimes]
  const lastHistValue = histFlows[histFlows.length - 1]
  const lastHistTime = histTimes[histTimes.length - 1]

  // 为了图表连续，将历史最后一项加入预测序列
  const finalPredTimes = [lastHistTime, ...predTimes]
  const finalPredFlows = [lastHistValue, ...predFlows]

  const histData = new Array(allTimes.length).fill(null)
  for(let i=0; i<histTimes.length; i++) {
    histData[i] = histFlows[i]
  }

  const predData = new Array(allTimes.length).fill(null)
  const offset = histTimes.length - 1
  for(let i=0; i<finalPredTimes.length; i++) {
    predData[offset + i] = finalPredFlows[i]
  }

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross', label: { backgroundColor: '#6a7985' } }
    },
    legend: {
      data: ['历史真实流量', '模型预测流量'],
      textStyle: { color: '#fff' },
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '15%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        boundaryGap: false,
        data: allTimes.map(t => t.substring(5, 16)), // MM-DD HH:mm
        axisLabel: { color: '#8892b0' },
        axisLine: { lineStyle: { color: '#334155' } }
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '车流量 (辆)',
        nameTextStyle: { color: '#8892b0' },
        axisLabel: { color: '#8892b0' },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
      }
    ],
    dataZoom: [
      { type: 'inside', start: 50, end: 100 },
      { start: 50, end: 100, handleIcon: 'path://M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z', handleSize: '80%', handleStyle: { color: '#fff', shadowBlur: 3, shadowColor: 'rgba(0, 0, 0, 0.6)', shadowOffsetX: 2, shadowOffsetY: 2 } }
    ],
    series: [
      {
        name: '历史真实流量',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 3, color: '#00ffff' },
        itemStyle: { color: '#00ffff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 255, 255, 0.5)' },
            { offset: 1, color: 'rgba(0, 255, 255, 0.01)' }
          ])
        },
        data: histData
      },
      {
        name: '模型预测流量',
        type: 'line',
        smooth: true,
        lineStyle: { width: 3, type: 'dashed', color: '#ff9900' },
        itemStyle: { color: '#ff9900' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255, 153, 0, 0.4)' },
            { offset: 1, color: 'rgba(255, 153, 0, 0.01)' }
          ])
        },
        data: predData
      },
      {
        // 呼吸灯特效，标注预测起始点
        name: '当前时刻',
        type: 'effectScatter',
        coordinateSystem: 'cartesian2d',
        data: [[formatTime(lastHistTime), lastHistValue]],
        symbolSize: 15,
        showEffectOn: 'render',
        rippleEffect: { brushType: 'stroke', scale: 3 },
        itemStyle: { color: '#00ffff', shadowBlur: 10, shadowColor: '#00ffff' }
      }
    ]
  }

  mainChartInstance.setOption(option)
}

const fetchData = async () => {
  loading.value = true
  try {
    const [historyRes, predictRes] = await Promise.all([
      axios.get('http://127.0.0.1:8000/api/history'),
      axios.get('http://127.0.0.1:8000/api/predict')
    ])
    
    const histData = historyRes.data
    const predData = predictRes.data
    
    // 更新指标
    metrics.rmse = predData.metrics.rmse
    metrics.mae = predData.metrics.mae
    metrics.confidence = predData.metrics.confidence
    ringConfig.data = [{ name: '预测置信度', value: metrics.confidence }]
    
    // 渲染图表
    initHistoryChart(histData.timestamps, histData.flow)
    
    loading.value = false
    // Vue 的 nextTick() 无法在此上下文中直接无缝使用，使用 setTimeout 延迟渲染大图
    setTimeout(() => {
      initMainChart(histData.timestamps, histData.flow, predData.timestamps, predData.predicted_flow)
    }, 100)

  } catch (error) {
    console.error("数据加载失败:", error)
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
  
  window.addEventListener('resize', () => {
    if (historyChartInstance) historyChartInstance.resize()
    if (mainChartInstance) mainChartInstance.resize()
  })
})

onUnmounted(() => {
  if (historyChartInstance) historyChartInstance.dispose()
  if (mainChartInstance) mainChartInstance.dispose()
})
</script>

<style scoped>
.dashboard-container {
  width: 100vw;
  height: 100vh;
  background-color: #020308;
  color: #fff;
  overflow: hidden;
}

.header {
  height: 80px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 20px;
  margin-bottom: 10px;
}

.header-decor-left, .header-decor-right {
  width: 300px;
  height: 50px;
}

.header-title {
  text-align: center;
  margin: 0 30px;
  flex: 1;
}

.header-title h2 {
  font-size: 32px;
  font-weight: bold;
  letter-spacing: 2px;
  background: linear-gradient(to bottom, #fff, #4fd2dd);
  -webkit-background-clip: text;
  color: transparent;
  margin: 0 0 10px 0;
}

.header-decor-center {
  width: 400px;
  height: 20px;
  margin: 0 auto;
}

.main-content {
  display: flex;
  height: calc(100vh - 100px);
  padding: 10px;
  box-sizing: border-box;
}

.side-panel {
  width: 25%;
  height: 100%;
}

.center-panel {
  width: 50%;
  height: 100%;
  margin: 0 15px;
}

.panel-inner {
  padding: 20px;
  height: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.panel-title {
  font-size: 18px;
  color: #3de7c9;
  text-align: center;
  margin: 0 0 15px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(61, 231, 201, 0.2);
}

.chart-box {
  flex: 1;
  width: 100%;
}

.main-chart-box {
  width: 100%;
  height: calc(100% - 30px);
}

.loading-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  font-size: 24px;
}

.metrics-container {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.metric-item {
  background: rgba(0, 186, 255, 0.1);
  border: 1px solid rgba(0, 186, 255, 0.3);
  border-radius: 8px;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  font-size: 16px;
  color: #a3b8cc;
}

.metric-value {
  font-size: 28px;
  font-weight: bold;
  color: #00ffff;
  font-family: 'Courier New', Courier, monospace;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
}

.confidence-container {
  margin-top: 40px;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.confidence-title {
  font-size: 16px;
  color: #a3b8cc;
  margin-bottom: 20px;
}
</style>
