// Vue应用配置
const { createApp } = Vue;

const API_BASE_URL = 'http://localhost:8000';

createApp({
    data() {
        return {
            currentPage: 'tasks',
            tasks: [],
            availableIndicators: [],
            selectedResult: null,
            systemStats: null,
            showCreateTask: false,
            radarChart: null,
            barChart: null,
            newTask: {
                name: '',
                description: '',
                agent_config: {
                    api_endpoint: '',
                    api_key: ''
                },
                dataset_config: {
                    type: 'json',
                    file_path: ''
                },
                selected_indicators: [],
                indicator_weights: {}
            },
            editingTask: null,
            showEditTask: false,
            indicatorCategories: [
                { key: 'basic_performance', name: '基础性能指标' },
                { key: 'generation_task', name: '生成任务指标' },
                { key: 'generalization', name: '通用化特征指标' },
                { key: 'custom', name: '自定义指标' }
            ]
        };
    },
    mounted() {
        this.loadTasks();
        this.loadIndicators();
        this.loadSystemStats();
        
        // 定期刷新任务列表
        setInterval(() => {
            if (this.currentPage === 'tasks') {
                this.loadTasks();
            }
        }, 5000);
    },
    methods: {
        // API调用方法
        async apiCall(endpoint, options = {}) {
            try {
                const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                    ...options,
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    }
                });
                
                if (!response.ok) {
                    const errorText = await response.text();
                    let errorMessage = `HTTP错误 ${response.status}`;
                    try {
                        const errorData = JSON.parse(errorText);
                        errorMessage = errorData.detail || errorData.message || errorMessage;
                    } catch {
                        errorMessage = errorText || errorMessage;
                    }
                    throw new Error(errorMessage);
                }
                
                return await response.json();
            } catch (error) {
                console.error('API调用失败:', error);
                // 不在这里自动alert，让调用方决定是否显示错误
                throw error;
            }
        },
        
        // 加载任务列表
        async loadTasks() {
            try {
                this.tasks = await this.apiCall('/api/tasks');
            } catch (error) {
                console.error('加载任务失败:', error);
            }
        },
        
        // 加载指标列表
        async loadIndicators() {
            try {
                this.availableIndicators = await this.apiCall('/api/indicators');
            } catch (error) {
                console.error('加载指标失败:', error);
            }
        },
        
        // 创建任务
        async createTask() {
            try {
                // 如果数据集路径为空，使用默认路径
                let datasetPath = this.newTask.dataset_config.file_path;
                if (!datasetPath || datasetPath.trim() === '') {
                    datasetPath = 'app/data/samples.json';  // 默认数据集路径
                }
                
                const taskData = {
                    name: this.newTask.name,
                    description: this.newTask.description,
                    agent_config: {
                        api_endpoint: this.newTask.agent_config.api_endpoint,
                        api_key: this.newTask.agent_config.api_key
                    },
                    dataset_config: {
                        type: this.newTask.dataset_config.type,
                        file_path: datasetPath.trim()
                    },
                    selected_indicators: this.newTask.selected_indicators,
                    indicator_weights: this.newTask.indicator_weights
                };
                
                await this.apiCall('/api/tasks', {
                    method: 'POST',
                    body: JSON.stringify(taskData)
                });
                
                this.showCreateTask = false;
                this.resetNewTask();
                this.loadTasks();
                alert('任务创建成功！');
            } catch (error) {
                console.error('创建任务失败:', error);
            }
        },
        
        // 重置新建任务表单
        resetNewTask() {
            this.newTask = {
                name: '',
                description: '',
                agent_config: {
                    api_endpoint: '',
                    api_key: ''
                },
                dataset_config: {
                    type: 'json',
                    file_path: ''
                },
                selected_indicators: [],
                indicator_weights: {}
            };
        },
        
        // 编辑任务
        async editTask(taskId) {
            try {
                console.log('开始编辑任务:', taskId);
                
                // 先重置状态
                this.showEditTask = false;
                this.editingTask = null;
                
                const task = await this.apiCall(`/api/tasks/${taskId}`);
                console.log('任务数据:', task);
                
                // 只允许编辑待执行或失败的任务
                if (task.status !== 'pending' && task.status !== 'failed') {
                    alert('只能编辑待执行或失败的任务');
                    return;
                }
                
                // 确保agent_config和dataset_config存在
                const agentConfig = task.agent_config || {};
                const datasetConfig = task.dataset_config || {};
                
                // 加载任务数据到编辑表单
                // 注意：API密钥出于安全考虑不显示，留空表示不修改
                this.editingTask = {
                    id: task.id,
                    name: task.name || '',
                    description: task.description || '',
                    agent_config: {
                        api_endpoint: agentConfig.api_endpoint || '',
                        api_key: ''  // 不显示原密钥，留空表示不修改
                    },
                    dataset_config: {
                        type: datasetConfig.type || 'json',
                        file_path: datasetConfig.file_path || ''
                    },
                    selected_indicators: Array.isArray(task.selected_indicators) ? task.selected_indicators : [],
                    indicator_weights: task.indicator_weights || {}
                };
                
                console.log('编辑任务数据已加载:', this.editingTask);
                
                // 使用$nextTick确保DOM更新
                this.$nextTick(() => {
                    this.showEditTask = true;
                    console.log('显示编辑模态框');
                });
            } catch (error) {
                console.error('加载任务失败:', error);
                alert('加载任务失败: ' + (error.message || '未知错误'));
            }
        },
        
        // 保存编辑的任务
        async saveEditedTask() {
            try {
                // 构建更新数据，API密钥如果为空则传递null（表示不修改）
                const taskData = {
                    name: this.editingTask.name,
                    description: this.editingTask.description,
                    agent_config: {
                        api_endpoint: this.editingTask.agent_config.api_endpoint,
                        api_key: this.editingTask.agent_config.api_key || null  // 空字符串转为null
                    },
                    dataset_config: {
                        type: this.editingTask.dataset_config.type,
                        file_path: this.editingTask.dataset_config.file_path
                    },
                    selected_indicators: this.editingTask.selected_indicators,
                    indicator_weights: this.editingTask.indicator_weights
                };
                
                await this.apiCall(`/api/tasks/${this.editingTask.id}`, {
                    method: 'PUT',
                    body: JSON.stringify(taskData)
                });
                
                this.showEditTask = false;
                this.editingTask = null;
                this.loadTasks();
                alert('任务配置已更新！');
            } catch (error) {
                console.error('更新任务失败:', error);
                alert('更新任务失败: ' + error.message);
            }
        },
        
        // 启动任务
        async startTask(taskId) {
            if (!confirm('确定要启动这个任务吗？')) {
                return;
            }
            
            try {
                await this.apiCall(`/api/tasks/${taskId}/start`, {
                    method: 'POST'
                });
                alert('任务已启动！');
                this.loadTasks();
            } catch (error) {
                console.error('启动任务失败:', error);
            }
        },
        
        // 删除任务
        async deleteTask(taskId) {
            if (!confirm('确定要删除这个任务吗？此操作不可恢复。')) {
                return;
            }
            
            try {
                await this.apiCall(`/api/tasks/${taskId}`, {
                    method: 'DELETE'
                });
                alert('任务已删除！');
                this.loadTasks();
            } catch (error) {
                console.error('删除任务失败:', error);
            }
        },
        
        // 查看任务详情和结果
        async viewTask(taskId) {
            try {
                const task = await this.apiCall(`/api/tasks/${taskId}`);
                
                // 如果任务失败，显示错误信息
                if (task.status === 'failed') {
                    const errorMsg = task.description && task.description.startsWith('执行失败:') 
                        ? task.description 
                        : '任务执行失败，请检查：\n1. 数据集路径是否正确\n2. API端点是否可访问\n3. 查看后端日志获取详细错误信息';
                    alert(errorMsg);
                    return;
                }
                
                if (task.result_id) {
                    const result = await this.apiCall(`/api/results/task/${taskId}`);
                    this.selectedResult = result;
                    this.currentPage = 'analysis';
                    // 等待DOM更新后渲染图表
                    this.$nextTick(() => {
                        setTimeout(() => {
                            this.renderRadarChart();
                        }, 100);
                    });
                } else {
                    if (task.status === 'completed') {
                        alert('任务已完成，但未生成结果，请检查后端日志。');
                    } else {
                        alert('该任务尚未完成，暂无结果。');
                    }
                }
            } catch (error) {
                console.error('查看任务失败:', error);
                alert('获取任务详情失败: ' + error.message);
            }
        },
        
        // 获取状态文本
        getStatusText(status) {
            const statusMap = {
                'pending': '等待中',
                'running': '执行中',
                'completed': '已完成',
                'failed': '失败',
                'cancelled': '已取消'
            };
            return statusMap[status] || status;
        },
        
        // 格式化日期
        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleString('zh-CN');
        },
        
        // 按类别获取指标
        getIndicatorsByCategory(category) {
            return this.availableIndicators.filter(ind => ind.category === category);
        },
        
        // 渲染雷达图
        renderRadarChart() {
            if (!this.selectedResult || !this.selectedResult.radar_chart_data) {
                return;
            }
            
            const ctx = document.getElementById('radarChart');
            if (!ctx) {
                return;
            }
            
            // 销毁旧图表
            if (this.radarChart) {
                this.radarChart.destroy();
            }
            
            const data = this.selectedResult.radar_chart_data;
            this.radarChart = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: data.labels || [],
                    datasets: data.datasets || []
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.dataset.label + ': ' + (context.parsed.r * 100).toFixed(1) + '%';
                                }
                            }
                        }
                    },
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 1,
                            ticks: {
                                stepSize: 0.2,
                                callback: function(value) {
                                    return (value * 100) + '%';
                                }
                            },
                            pointLabels: {
                                font: {
                                    size: 12
                                }
                            }
                        }
                    }
                }
            });
            
            // 渲染柱状图
            this.renderBarChart();
        },
        
        // 渲染柱状图
        renderBarChart() {
            if (!this.selectedResult || !this.selectedResult.result_items) {
                return;
            }
            
            const ctx = document.getElementById('barChart');
            if (!ctx) {
                return;
            }
            
            // 销毁旧图表
            if (this.barChart) {
                this.barChart.destroy();
            }
            
            const labels = this.selectedResult.result_items.map(item => item.indicator_name);
            const scores = this.selectedResult.result_items.map(item => item.score * 100);
            
            // 根据得分设置颜色
            const backgroundColors = scores.map(score => {
                if (score >= 80) return 'rgba(46, 204, 113, 0.8)';  // 绿色
                if (score >= 60) return 'rgba(241, 196, 15, 0.8)';  // 黄色
                return 'rgba(231, 76, 60, 0.8)';  // 红色
            });
            
            this.barChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '得分 (%)',
                        data: scores,
                        backgroundColor: backgroundColors,
                        borderColor: backgroundColors.map(c => c.replace('0.8', '1')),
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return '得分: ' + context.parsed.y.toFixed(1) + '%';
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            },
                            title: {
                                display: true,
                                text: '得分 (%)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: '评估指标'
                            }
                        }
                    }
                }
            });
        },
        
        // 获取得分等级
        getScoreClass(score) {
            if (score >= 0.8) return 'score-excellent';
            if (score >= 0.6) return 'score-good';
            if (score >= 0.4) return 'score-fair';
            return 'score-poor';
        },
        
        getScoreDescription(score) {
            if (score >= 0.8) return '优秀';
            if (score >= 0.6) return '良好';
            if (score >= 0.4) return '一般';
            return '需改进';
        },
        
        getLevelClass(score) {
            if (score >= 0.8) return 'level-excellent';
            if (score >= 0.6) return 'level-good';
            if (score >= 0.4) return 'level-fair';
            return 'level-poor';
        },
        
        getLevelText(score) {
            if (score >= 0.8) return '优秀';
            if (score >= 0.6) return '良好';
            if (score >= 0.4) return '一般';
            return '需改进';
        },
        
        // 获取最高得分
        getMaxScore(resultItems) {
            if (!resultItems || resultItems.length === 0) return 0;
            return Math.max(...resultItems.map(item => item.score));
        },
        
        // 获取最低得分
        getMinScore(resultItems) {
            if (!resultItems || resultItems.length === 0) return 0;
            return Math.min(...resultItems.map(item => item.score));
        },
        
        // 加载系统统计
        async loadSystemStats() {
            try {
                this.systemStats = await this.apiCall('/api/system/stats');
            } catch (error) {
                console.error('加载系统统计失败:', error);
            }
        },
        
        // 刷新系统统计
        refreshSystemStats() {
            this.loadSystemStats();
            alert('统计信息已刷新！');
        },
        
        // 格式化字节
        formatBytes(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
        }
    },
    watch: {
        currentPage(newPage) {
            if (newPage === 'system') {
                this.loadSystemStats();
            }
        }
    }
}).mount('#app');

