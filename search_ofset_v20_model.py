class MeasuredData():
    def __init__(self):
        # Sensor postion
        self.sensor_pos = [
            ['MD',44865],
            ['M_EMS',44705],
            ['COOLWATER2_1',44025],
            ['COOLWATER2_1',44025],
            ['COOLWATER2_2',43493],
            ['COOLWATER2_3',42595],
            ['COOLWATER2_4',41448],
            ['S_EMS',40635],
            ['PR_38',30990],
            ['PR_40',27990],
            ['LPSF_TEMP',22817],
            ['LOWPRS_43',22222],
            ['LOWPRS_44',21542],
            ['LOWPRS_45',20862],
            ['LOWPRS_46',20182],
            ['LOWPRS_47',19502],
            ['LOWPRS_48',18822],
            ['LOWPRS_49',18141],
            ['LOWPRS_50',17462],
            ['LOWPRS_51',16782],
            ['LOWPRS_52',16102],
            ['LOWPRS_53',15422],
            ['LOWPRS_54',14742],
            ['LOWPRS_55',14062],
            ['LOWPRS_56',13382],
            ['LOWPRS_57',12702],
            ['LOWPRS_58',12022],
            ['HPSF_TEMP',9570],
            ['HIGPRS_60',7985],
            ['MR',2778]
        ]

        # pool data array limit
        self.max_items = 15661
        
        # line counter
        self.ln_cnt =0

        # cut off counter
        self.cut_cnt =0

        # 1 line values arrey
        self.line_buf = []

        # Previous line values arrey
        self.bf_line_buf = ['Null'] * 691

        # All stack data
        self.pool_data = [[]]

        # Output data (Return values to Data bus)
        # productNo,sensorPosName,time,values
        self.output_data = [[]]
        
    def edge_predict(self,input):
        self.line_buf = input
        
        # Check array limit
        if (len(self.pool_data) >= self.max_items):
            self.pool_data.pop(0)
            
        self.pool_data.append(input)

        self.return_val = [[]]

        # Check cut off
        # cutting 1 -> 0
        # complete 0 -> 1
        if (self.bf_line_buf[641] == '1' and self.line_buf[641] == '0'
            and self.bf_line_buf[644] == '0' and self.line_buf[644] == '1'):
            cutoff_buf = [self.line_buf[0],self.line_buf[3],self.line_buf[5],self.line_buf[537],self.line_buf[538],self.line_buf[555]]
            self.cut_cnt += 1

            for ssr in range(len(self.sensor_pos)):
                if (int(cutoff_buf[1]) - int(cutoff_buf[5]) - self.sensor_pos[ssr][1] - int(cutoff_buf[4]) >= 0):
                    # Ingestion start position on the Sensor
                    st_pos = int(cutoff_buf[1]) - int(cutoff_buf[5]) - self.sensor_pos[ssr][1] - int(cutoff_buf[4])

                    # Ingestion end position on the Sensor
                    ed_pos = int(cutoff_buf[1]) - int(cutoff_buf[5]) - self.sensor_pos[ssr][1]

                    # Search Ingestion start time
                    for buf in range(len(self.pool_data)):
                        if (buf > 1 and self.pool_data[buf - 1][3] != 'nan' and self.pool_data[buf][3] != 'nan'):
                            if (int(self.pool_data[buf - 1][3]) <= st_pos < int(self.pool_data[buf][3])):
                                strow_no = buf - 1
                                break

                    # Search Ingestion end time
                    for buf in range(len(self.pool_data)):
                        if (buf > 1 and self.pool_data[buf - 1][3] != 'nan' and self.pool_data[buf][3] != 'nan'):
                            if (int(self.pool_data[buf - 1][3]) < ed_pos <= int(self.pool_data[buf][3])):
                                edrow_no = buf
                                break

                    # search Target data
                    target = False
                    for buf in range(len(self.pool_data)):
                        if (buf > 1 and self.pool_data[buf - 1][3] != 'nan' and self.pool_data[buf][3] != 'nan'):
                            # Start position on Target data
                            if (int(self.pool_data[buf - 1][3]) <= st_pos < int(self.pool_data[buf][3])):
                                target = True
                                self.output_data = [[]]
                                wk_ary = []

                                # MR value:534,535
                                if (self.sensor_pos[ssr][0] == 'MR'):
                                    wk_ary = [cutoff_buf[3],self.sensor_pos[ssr][0],self.pool_data[buf - 1][0]]
                                    wk_ary.extend(self.pool_data[buf - 1][534:536])

                                # HIGPRS_60 value:506-533
                                if (self.sensor_pos[ssr][0] == 'HIGPRS_60'):
                                    wk_ary = [cutoff_buf[3],self.sensor_pos[ssr][0],self.pool_data[buf][0]]
                                    wk_ary.extend(self.pool_data[buf - 1][506:534])

                                if (len(wk_ary) > 0):
                                    self.output_data.append(wk_ary)

                            if (target):
                                # MR value:534,535
                                if (self.sensor_pos[ssr][0] == 'MR'):
                                    wk_ary = [cutoff_buf[3],self.sensor_pos[ssr][0],self.pool_data[buf][0]]
                                    wk_ary.extend(self.pool_data[buf][534:536])

                                # HIGPRS_60 value:506-533
                                if (self.sensor_pos[ssr][0] == 'HIGPRS_60'):
                                    wk_ary = [cutoff_buf[3],self.sensor_pos[ssr][0],self.pool_data[buf][0]]
                                    wk_ary.extend(self.pool_data[buf][506:534])

                                if (len(wk_ary) > 0):
                                    self.output_data.append(wk_ary)

                            # End position on Target data
                            if (int(self.pool_data[buf - 1][3]) < ed_pos <= int(self.pool_data[buf][3])):
                                target = False

                                # Print target data on each sensor postion
                                # Return to data bus
                                if (len(self.output_data) > 1):
                                    self.output_data.pop(0)
#                                    for vals in output_data:
#                                        print vals
                                    
#                                    self.return_val += self.output_data
                                    self.return_val.extend(self.output_data)
                                break
                # There is no correct position data
                else:
                    self.return_val.append([cutoff_buf[3],self.sensor_pos[ssr][0],'No data on the sensor position'])
        # It's not s cut-off point    
        else:
            self.return_val += ['Out of Target']
            
        self.ln_cnt += 1
        self.bf_line_buf = self.line_buf

        """
        print("=============================================")
        print("Read line total : {0}".format(self.ln_cnt))
        """
        
        # Pop out initial value
        self.return_val.pop(0)
        
        return self.return_val
