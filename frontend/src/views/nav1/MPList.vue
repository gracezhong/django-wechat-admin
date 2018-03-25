<template>
	<section>
		<!--工具条-->
		<el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
			<el-form :inline="true" :model="filters">
				<el-form-item>
					<el-input v-model="filters.name" placeholder="姓名" clearable></el-input>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" v-on:click="getMPs">查询</el-button>
				</el-form-item>
			</el-form>
		</el-col>

		<!--列表-->
		<el-table :data="mps" highlight-current-row v-loading="listLoading" @selection-change="selsChange" style="width: 100%;">
			<el-table-column type="selection" width="55">
			</el-table-column>
			<el-table-column type="index" width="60">
			</el-table-column>
			<el-table-column prop="nick_name" label="名称" width="150" sortable>
			</el-table-column>
			<el-table-column prop="province" label="省份" width="100" sortable>
			</el-table-column>
			<el-table-column prop="city" label="城市" width="100" sortable>
			</el-table-column>
			<el-table-column prop="signature" label="个性签名" min-width="200" sortable show-overflow-tooltip>
			</el-table-column>
			<el-table-column label="操作" min-width="60">
				<template slot-scope="scope">
					<el-button size="small" width="50" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
					<el-button type="danger" width="50" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
				</template>
			</el-table-column>
		</el-table>

		<!--工具条-->
		<el-col :span="24" class="toolbar">
			<el-button type="danger" @click="batchRemove" :disabled="this.sels.length===0">批量删除</el-button>
			<el-pagination background layout="prev, pager, next" @size-change="handleSizeChange" @current-change="handleCurrentChange" :page-size="pageSize" :total="total" style="float:right;">
			</el-pagination>
		</el-col>

		<!--编辑界面-->
		<el-dialog title="编辑" v-model="editFormVisible" :close-on-click-modal="false">
			<el-form :model="editForm" label-width="80px" :rules="editFormRules" ref="editForm">
				<el-form-item label="用户名" prop="nick_name">
					<el-input v-model="editForm.nick_name" auto-complete="off"></el-input>
				</el-form-item>
				<el-form-item label="密码" prop="password">
					<el-input type="password" v-model="editForm.password" auto-complete="off"></el-input>
				</el-form-item>
				<el-form-item label="员工">
					<el-radio-group v-model="editForm.is_staff">
						<el-radio class="radio" :label="true">是</el-radio>
						<el-radio class="radio" :label="false">否</el-radio>
					</el-radio-group>
				</el-form-item>
				<el-form-item label="邮箱">
					<el-input v-model="editForm.email" auto-complete="off"></el-input>
				</el-form-item>
				<el-form-item label="手机">
					<el-input v-model="editForm.phone" auto-complete="off"></el-input>
				</el-form-item>
				<el-form-item label="自我介绍">
					<el-input type="textarea" v-model="editForm.description"></el-input>
				</el-form-item>
			</el-form>
			<div slot="footer" class="dialog-footer">
				<el-button @click.native="editFormVisible = false">取消</el-button>
				<el-button type="primary" @click.native="editSubmit" :loading="editLoading">提交</el-button>
			</div>
		</el-dialog>

	</section>
</template>

<script>
	import util from '../../common/js/util'
	import { getMPListPage } from '../../api/api';

	export default {
		data() {
			return {
				filters: {
					name: ''
				},
				mps: [],
				total: 0,
				page: 1,
				pageSize: 10,
				listLoading: false,
				sels: [],//列表选中列

				editFormVisible: false,//编辑界面是否显示
				editLoading: false,
				editFormRules: {
					nick_name: [{ required: true, message: '请输入用户名', trigger: 'blur' }]
				},
				//编辑界面数据
				editForm: {
					id: 0,
					nick_name: '',
					is_staff: -1,
					email: null,
					description: null,
					phone: null
				},

			}
		},
		methods: {
			//显示转换
            formatSex: function(row) {
                return row.sex == 1 ? '男' : row.sex == 2? '女' : '';
			},
            handleSizeChange(val) {
                this.pageSize = val;
			},
			handleCurrentChange(val) {
				this.page = val;
				this.getMPs();
			},
			//获取用户列表
			getMPs() {
				let para = {
					page: this.page,
					page_size: this.pageSize,
                    nick_name__contains: this.filters.name
				};
				this.listLoading = true;
				//NProgress.start();
				getMPListPage(para).then((res) => {
				    console.log("get page data");
				    console.log(para);
				    console.log(res);
					this.total = res.data.count;
					this.mps = res.data.results;
					this.listLoading = false;
					//NProgress.done();
				});
			},
			//删除
			handleDel: function (index, row) {
				this.$confirm('确认删除该记录吗?', '提示', {
					type: 'warning'
				}).then(() => {
					this.listLoading = true;
					//NProgress.start();
					let para = { id: row.id };
					// removeUser(para).then((res) => {
					// 	this.listLoading = false;
					// 	console.log(res);
					// 	//NProgress.done();
					// 	this.$message({
					// 		message: '删除成功',
					// 		type: 'success'
					// 	});
					// 	this.getMPs();
					// });
				}).catch(() => {

				});
			},
			//显示编辑界面
			handleEdit: function (index, row) {
                console.log(this.editForm);
				// this.editForm = Object.assign({}, row);
                this.editForm.puid = row.puid;
				this.editForm.nick_name = row.nick_name;
				// console.log(this.editForm);
                this.editFormVisible = true;
			},
			//编辑
			editSubmit: function () {
				this.$refs.editForm.validate((valid) => {
					if (valid) {
						this.$confirm('确认提交吗？', '提示', {}).then(() => {
							this.editLoading = true;
							let para = Object.assign({}, this.editForm);
							// console.log(this.editForm);
                            console.log('Edit MP info parameters:');
							console.log(para);
						});
					}
				});
			},
			selsChange: function (sels) {
				this.sels = sels;
			},
			//批量删除
			batchRemove: function () {
				var ids = this.sels.map(item => item.id).toString();
				this.$confirm('确认删除选中记录吗？', '提示', {
					type: 'warning'
				}).then(() => {
					this.listLoading = true;
					let para = { ids: ids };
					console.log(para.ids);
				})
			}
		},
		mounted() {
			this.getMPs();
		}
	}

</script>

<style scoped>

</style>