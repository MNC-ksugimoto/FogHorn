# -*- coding: utf-8 -*-
#############################################################
#
# 【愛知製鋼】切断鋳片の過去計測値の場所特定、データ取得のモデル
#  search on reverse loop
#
#  総鋳造長のサイクリック変化への対応
#    直前の値より小さい場合は、直前の値に自身の値を加えたものを総鋳造長とする。
#
#############################################################
class MeasuredData2():
    def __init__(self):
        # Sensor postion
        self.sensor_pos = [
            ['MR',2778],
            ['HIGPRS_60',7985],
            ['HPSF_TEMP',9570],
            ['LOWPRS_58',12022],
            ['LOWPRS_57',12702],
            ['LOWPRS_56',13382],
            ['LOWPRS_55',14062],
            ['LOWPRS_54',14742],
            ['LOWPRS_53',15422],
            ['LOWPRS_52',16102],
            ['LOWPRS_51',16782],
            ['LOWPRS_50',17462],
            ['LOWPRS_49',18141],
            ['LOWPRS_48',18822],
            ['LOWPRS_47',19502],
            ['LOWPRS_46',20182],
            ['LOWPRS_45',20862],
            ['LOWPRS_44',21542],
            ['LOWPRS_43',22222],
            ['LPSF_TEMP',22817],
            ['PR_40',27990],
            ['PR_38',30990],
            ['S_EMS',40635],
            ['COOLWATER2_4',41448],
            ['COOLWATER2_3',42595],
            ['COOLWATER2_2',43493],
            ['COOLWATER2_1',44025],
            ['M_EMS',44705],
            ['MD',44865],
        ]

        # target cell point of the total length value
        self.tl_point = 692
        
        # pool data array limit
        self.max_items = 15661
        
        # line counter
        self.ln_cnt =0

        # cut off counter
        self.cut_cnt =0

        # 1 line values arrey
#        self.line_buf = []

        # Previous line values arrey
        self.bf_line_buf = ['Null'] * 693

        # All stack data
        self.pool_data = [[]]

        # Output data (Return values to Data bus)
        # productNo,sensorPosName,time,values
        self.output_data = [[]]
        
    def edge_predict(self,input):
        line_buf = [input[0]]
        line_buf.extend(input[1:])
        line_buf.extend(input[3:4])
        """
        # Why does not work well as bellow on Edge ML ?
        line_buf = input[:]
        line_buf.extend(input[3:4])
        # 'numpy.ndarray' object has no attribute 'extend'
        """
        
        # cumulative total lenght
        if (self.bf_line_buf[self.tl_point] != 'Null'):
            if (long(self.bf_line_buf[3]) > long(line_buf[3])):
                line_buf[self.tl_point] = str(long(self.bf_line_buf[self.tl_point]) + long(line_buf[3]))
            elif (long(self.bf_line_buf[3]) < long(self.bf_line_buf[self.tl_point])):
                line_buf[self.tl_point] = str(long(self.bf_line_buf[self.tl_point]) + long(line_buf[3]) - long(self.bf_line_buf[3]))
        
#        print("[3]:{0} -> [692]{1}".format(self.line_buf[3],self.line_buf[self.tl_point]))
        
        # Check array limit
        if (len(self.pool_data) >= self.max_items):
            self.pool_data.pop(0)
            
        self.pool_data.append(line_buf)

        self.return_val = [[]]
        wk_ary = []

        # Check cut off
        # 切断中 1 -> 0
        # 切断完了 0 -> 1
        if (self.bf_line_buf[641] == '1' and line_buf[641] == '0'
            and self.bf_line_buf[644] == '0' and line_buf[644] == '1'):
            # time,総鋳造長,pv値,BL-No.,切断長,台車位置,累積総鋳造長
            cutoff_buf = [line_buf[0],line_buf[3],line_buf[5],line_buf[537],line_buf[538],line_buf[555],line_buf[self.tl_point]]
            self.cut_cnt += 1

            for ssr in range(len(self.sensor_pos)):
                if (long(cutoff_buf[6]) - long(cutoff_buf[5]) - self.sensor_pos[ssr][1] - long(cutoff_buf[4]) >= 0):
                    # Ingestion start position on the Sensor
                    st_pos = long(cutoff_buf[6]) - long(cutoff_buf[5]) - self.sensor_pos[ssr][1] - long(cutoff_buf[4])

                    # Ingestion end position on the Sensor
                    ed_pos = long(cutoff_buf[6]) - long(cutoff_buf[5]) - self.sensor_pos[ssr][1]

                    """
                    print('\n【{0}】開始位置 tl_pos[{1}]:{2}'.format(cutoff_buf[3],self.sensor_pos[ssr][0],st_pos))
                    print('【{0}】終了位置 tl_pos[{1}]:{2}'.format(cutoff_buf[3],self.sensor_pos[ssr][0],ed_pos))
                    """

                    # Search Ingestion end time
                    edrow_no = 0
                    strow_no = 0
                    for buf in range(-1,(len(self.pool_data)-1)* -1,-1):
                        if (self.pool_data[buf - 1][3] != 'nan' and self.pool_data[buf][3] != 'nan'):
                            # Search Ingestion end time
                            if ((long(self.pool_data[buf - 1][self.tl_point]) < ed_pos <= long(self.pool_data[buf][self.tl_point])) and edrow_no == 0):
                                edrow_no = buf

                            # Search Ingestion start time
                            if ((long(self.pool_data[buf - 1][self.tl_point]) <= st_pos < long(self.pool_data[buf][self.tl_point])) and strow_no == 0):
                                strow_no = buf - 1

#                            print("edrow_no:{0} - strow_no:{1}".format(edrow_no,strow_no))
                            
                            if (edrow_no * strow_no > 0):
                                """
                                print('【{0}】終了時刻[{1}] tl_pos[{2}]:{3}'.format(cutoff_buf[3],edrow_no,self.sensor_pos[ssr][0],self.pool_data[edrow_no][0]))
                                print('【{0}】開始時刻[{1}] tl_pos[{2}]:{3}'.format(cutoff_buf[3],strow_no,self.sensor_pos[ssr][0],self.pool_data[strow_no][0]))
                                """
                                break

                    # search Target data
                    target = False
                    for buf in range(-1,(len(self.pool_data)-1)* -1,-1):
                        if (self.pool_data[buf - 1][3] != 'nan' and self.pool_data[buf][3] != 'nan'):
                            # End position on Target data
                            if (long(self.pool_data[buf - 1][self.tl_point]) < ed_pos <= long(self.pool_data[buf][self.tl_point])):
                                target = True
                                self.output_data = [[]]
                                
                            if (target):
                                wk_ary = [cutoff_buf[3],self.sensor_pos[ssr][0],self.pool_data[buf][0]]

                                # MR value:534,535
                                if (self.sensor_pos[ssr][0] == 'MR'):
                                    wk_ary.extend(self.pool_data[buf][534:536])

                                # HIGPRS_60 value:506-533
                                if (self.sensor_pos[ssr][0] == 'HIGPRS_60'):
                                    wk_ary.extend(self.pool_data[buf][506:534])

                                self.output_data.append(wk_ary)

                            # Start position on Target data
                            if (long(self.pool_data[buf - 1][self.tl_point]) <= st_pos < long(self.pool_data[buf][self.tl_point])):
                                target = False
                                wk_ary = [cutoff_buf[3],self.sensor_pos[ssr][0],self.pool_data[buf-1][0]]

                                # MR value:534,535
                                if (self.sensor_pos[ssr][0] == 'MR'):
                                    wk_ary.extend(self.pool_data[buf - 1][534:536])

                                # HIGPRS_60 value:506-533
                                if (self.sensor_pos[ssr][0] == 'HIGPRS_60'):
                                    wk_ary.extend(self.pool_data[buf - 1][506:534])

                                self.output_data.append(wk_ary)

                                # Print target data on each sensor postion
                                # Return to data bus
                                if (len(self.output_data) > 1):
                                    self.output_data.pop(0)
                                    self.return_val.extend(self.output_data)

                                break

                    if (edrow_no * strow_no == 0):
                        self.return_val.append([cutoff_buf[3],self.sensor_pos[ssr][0],'No data on the sensor position'])
                    
                # There is no correct position data
                else:
                    self.return_val.append([cutoff_buf[3],self.sensor_pos[ssr][0],'No data on the sensor position'])
        # It's not s cut-off point    
        else:
            self.return_val += ['Out of Target']
            
        self.ln_cnt += 1
        self.bf_line_buf = line_buf[:]

        """
        print("=============================================")
        print("Read line total : {0}".format(self.ln_cnt))
        """
        
        # Pop out initial value
        self.return_val.pop(0)
        
        return self.return_val
