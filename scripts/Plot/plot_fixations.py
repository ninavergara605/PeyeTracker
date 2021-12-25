import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scripts.PathUtilities.general_path_functions import create_path


class PlotFixations:


    def __init__(self, fixations, roi,res_directory, group_by=[],shape=None, show_legend=True):
        fixations.reset_index(level='file_position', inplace=True, drop=True)
        self.fixations = fixations.reset_index()
        self.roi = roi.reset_index()
        self.res_directory = res_directory
        self.show_legend = show_legend
        
        if shape:
            self.shape = shape
        else:
            self.shape = (3,2)
        if group_by:
            self.group_by = group_by
        else:
            self.group_by = fixations.index.names
        self.dispatch()

    def dispatch(self):
        fix_sorted = self.fixations.sort_values(self.group_by)
        page_max = (self.shape[0] * self.shape[1]) - 1

        _, axs = plt.subplots(*self.shape)
        axes = axs.flatten()
        for name, group in fix_sorted.groupby(self.group_by[:-1]):
           if isinstance(name, (int, float)):
               name = [name]
           plot_groups = group.groupby(self.group_by[-1])
           counter=0
           plot_ids = []
           
           for name_2,_group in plot_groups:
                if counter > page_max:
                    
                    self.export(plot_ids, name)
                    plot_ids = []
                    counter=0
                    _, axs = plt.subplots(*self.shape)
                    axes = axs.flatten()
                self.plot(list(name)+[name_2],_group, axes[counter])
                counter += 1
                plot_ids.append(name_2)
           self.export(plot_ids, name)

    def export(self, plot_ids, name):
        if not plot_ids:
            return
        file_name = ''.join([f'{label}: {str(value)} ' 
                        for label, value in zip(self.group_by[-1], name)
                    ])
        if isinstance(plot_ids[0], (int, float)):
            file_name += f'{self.group_by[-1]}: {str(plot_ids[0])}-{str(plot_ids[-1])}'
        else:
            file_name += f"{self.group_by[-1]}: {','.join(plot_ids)}"
        full_path = create_path(self.res_directory, file_name=file_name,folder='plot_fixations',extension='.png')
        plt.savefig(full_path)

    def plot(self, filter_by, subj_points, ax):
        title = ''.join([label +': ' + str(value) +' '
                             for label, value in zip(self.group_by, filter_by)])
        ax.set_title(title)
        
        ax.scatter(subj_points.x, subj_points.y, color='black', s=0.5)
       
        if not self.roi.empty:
            rectangles = self.create_roi_patches(filter_by)
            for rect in rectangles:
                ax.add_patch(rect)

        ax.set_xlim(0,1600)
        ax.set_ylim(0,1100)
        ax.invert_yaxis()

    def create_roi_patches(self, sub_filter):
        subj_roi = self.roi[self.roi[self.group_by].values== sub_filter]
        width = subj_roi.bottom_right_x - subj_roi.top_left_x
        height = -(subj_roi.bottom_right_y-subj_roi.top_left_y)
        
        ax1_patches = []
        anchors = zip(subj_roi.top_left_x.values, subj_roi.bottom_right_y.values)
        for anchor, _width, _height in  zip(anchors, width.values, height.values):
            ax1_patches.append(Rectangle(anchor, _width, _height, facecolor='none', edgecolor='black'))
        return ax1_patches